require('dotenv').config();
const express = require('express');
const line = require('@line/bot-sdk');
const axios = require('axios');
const db = require('./db');

const config = {
    channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN,
    channelSecret: process.env.LINE_CHANNEL_SECRET,
};

const HF_TOKEN = process.env.HUGGINGFACE_API_TOKEN;

const app = express();
app.use(express.json());

const client = new line.messagingApi.MessagingApiClient({
    channelAccessToken: config.channelAccessToken
});

app.post('/webhook', (req, res) => {
    if (!req.body || !req.body.events) {
        return res.status(400).send('Bad Request');
    }
    const events = req.body.events;
    for (const event of events) {
        if (event.type === 'message' && event.message.type === 'text') {
            // 立即回 200，不要 await 長時間處理（HF 可能花時間），但 handle 內會盡快用 replyToken 回覆
            handleMessage(event).catch(err => console.error('handleMessage 未預期錯誤:', err));
        }
    }
    res.sendStatus(200);
});

async function handleMessage(event) {
    try {
        const text = (event.message.text || '').trim();
        const replyToken = event.replyToken;

        if (!replyToken) {
            console.log('缺少 replyToken，無法回覆');
            return;
        }

        console.log(`收到訊息: ${text}`);

        let replyText;
        if (['作業', '今天作業'].some(k => text.includes(k))) {
            const msg = await getAssignments();
            replyText = msg && msg.text ? msg.text : '目前沒有作業資料';
        } 
        else if (text.includes('課表')) {
            const msg = await getCourses(text);
            replyText = msg && msg.text ? msg.text : '目前沒有課表';
        }
        else {
            const aiReply = await callHuggingFace(text);
            replyText = aiReply;
        }

        // 確保回覆文字永遠合法（非空、合理長度）
        let safeText = (replyText || '好的').toString().trim();
        if (!safeText) safeText = '好的';
        if (safeText.length > 5000) safeText = safeText.slice(0, 4997) + '...';

        await client.replyMessage({ replyToken, messages: [{ type: 'text', text: safeText }] });
    } catch (err) {
        console.error('handleMessage 發生錯誤:', err.message);
        // 不要 rethrow，避免 webhook 回 500 導致 LINE 重試事件
    }
}

// 查詢作業
async function getAssignments() {
    try {
        const rows = await db.allAsync("SELECT * FROM assignments ORDER BY due_date LIMIT 10");
        if (rows.length === 0) return { type: 'text', text: '目前沒有作業資料' };

        let msg = "📚 近期作業\n\n";
        rows.forEach(r => {
            msg += `📝 ${r.title}\n   📅 ${r.due_date}\n   📌 ${r.course_name}\n\n`;
        });
        return { type: 'text', text: msg };
    } catch (e) {
        return { type: 'text', text: '查詢作業失敗' };
    }
}

const WEEKDAY = ['', '一', '二', '三', '四', '五', '六', '日'];

// 簡稱 → 資料庫 department 關鍵字（LIKE）
const DEPT_ALIASES = {
    '中文': '中國文學',
    '企管': '企業管理',
    '德文': '德國文化',
    '日文': '日本語文',
    '外文': '外文',
    '資科': '資料科學',
    '資管': '資訊管理',
    '財精': '財務工程',
    '華語': '華語教學',
    '社工': '社會工作',
    '微生物': '微生物',
};

function parseTimetableQuery(text) {
    const rest = text.replace(/課表/g, '').trim();
    if (!rest) return { mode: 'list' };

    const classMatch = rest.match(/([\u4e00-\u9fff0-9Ａ-ＺA-Z]+班)/);
    if (classMatch) return { mode: 'class', keyword: classMatch[1] };

    const deptMatch = rest.match(/([\u4e00-\u9fff]+(?:學系|學程|學院|系|院)?)/);
    if (deptMatch) {
        const kw = deptMatch[1].replace(/系$/, '');
        return { mode: 'dept', keyword: kw };
    }
    return { mode: 'dept', keyword: rest };
}

async function resolveDepartment(keyword) {
    const rows = await db.allAsync(
        `SELECT DISTINCT department FROM timetable WHERE semester = '114-2' ORDER BY department`
    );
    const names = rows.map(r => r.department);
    if (names.includes(keyword)) return keyword;
    const alias = DEPT_ALIASES[keyword];
    if (alias) {
        const hit = names.find(d => d.includes(alias));
        if (hit) return hit;
    }
    const hit = names.find(d => d.includes(keyword) || keyword.includes(d.replace(/學系|學院/g, '')));
    return hit || null;
}

async function getCourses(text = '') {
    try {
        const q = parseTimetableQuery(text);

        if (q.mode === 'list') {
            const depts = await db.allAsync(`
                SELECT department, COUNT(*) AS cnt
                FROM timetable
                WHERE semester = '114-2'
                GROUP BY department
                ORDER BY department
            `);
            if (!depts.length) {
                return { type: 'text', text: '資料庫沒有 114-2 課表，請執行 import_to_db.py --replace' };
            }
            let msg = '📋 114-2 可查詢科系（共 ' + depts.length + ' 個）\n\n';
            depts.forEach(d => {
                msg += `• ${d.department}（${d.cnt} 筆）\n`;
            });
            msg += '\n請輸入：課表 資料科學系\n或：課表 資科一Ａ';
            return { type: 'text', text: msg.trim() };
        }

        let sql = `
            SELECT course_name, teacher, class_name, day_of_week, start_time, end_time, classroom, department
            FROM timetable
            WHERE semester = '114-2'
        `;
        const params = [];
        let title = '';

        if (q.mode === 'class') {
            sql += ` AND class_name LIKE ?`;
            params.push('%' + q.keyword + '%');
            title = q.keyword;
        } else {
            const dept = await resolveDepartment(q.keyword);
            if (!dept) {
                return {
                    type: 'text',
                    text: `找不到「${q.keyword}」對應科系。\n請先傳「課表」看完整科系列表，或輸入「課表 資料科學系」。`,
                };
            }
            sql += ` AND department = ?`;
            params.push(dept);
            title = dept;
        }
        sql += ` ORDER BY class_name, day_of_week, start_time LIMIT 80`;

        const rows = await db.allAsync(sql, params);
        if (!rows.length) {
            return { type: 'text', text: `「${title}」在資料庫沒有課表（114-2）。` };
        }

        let msg = `📅 ${title} 課表（114-2）\n\n`;
        rows.forEach(r => {
            const wd = WEEKDAY[r.day_of_week] || '?';
            msg += `【${r.class_name}】${r.course_name}\n`;
            msg += `  週${wd} ${r.start_time}-${r.end_time} ${r.classroom || ''}\n`;
            msg += `  ${r.teacher || '未定'}\n\n`;
        });
        if (rows.length >= 80) msg += '（僅顯示前 80 筆）';
        return { type: 'text', text: msg.trim() };
    } catch (e) {
        console.error('getCourses 錯誤:', e.message);
        return { type: 'text', text: '查詢課表失敗' };
    }
}

async function callHuggingFace(msg) {
    if (!HF_TOKEN) {
        return 'AI 功能尚未設定 API Token。';
    }
    try {
        const res = await axios.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", {
            inputs: `<s>[INST] 你是大學生活助理，用口語回答：${msg} [/INST]`,
            parameters: { max_new_tokens: 200, temperature: 0.7, return_full_text: false }
        }, { 
            headers: { Authorization: `Bearer ${HF_TOKEN}` },
            timeout: 12000  // 避免超過 LINE replyToken 有效時間
        });

        let generated = '';
        if (Array.isArray(res.data) && res.data[0]?.generated_text) {
            generated = res.data[0].generated_text;
        } else if (res.data && res.data.generated_text) {
            generated = res.data.generated_text;
        } else if (typeof res.data === 'string') {
            generated = res.data;
        }

        // 優先取 [/INST] 之後的內容；若無則用整個；並清理常見 token
        let reply = generated.split('[/INST]').pop()?.trim() || generated.trim() || '';
        reply = reply.replace(/<\/?s>|<\/?\|.*?\|>|<\|.*?\|>/g, '').trim();

        if (!reply) reply = '好的';
        if (reply.length > 2000) reply = reply.slice(0, 1997) + '...';
        return reply;
    } catch (e) {
        if (e.code === 'ECONNABORTED' || e.message.includes('timeout')) {
            console.log('HF 呼叫逾時');
        } else {
            console.log('HF 呼叫失敗:', e.message);
        }
        return 'AI 忙線中，請再試一次。';
    }
}

// 啟動
app.listen(3000, () => {
    console.log(`🚀 大學助理 Bot 已啟動！`);
    console.log(`📡 本地端口: 3000`);
});