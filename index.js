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
            const msg = await getCourses();
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

async function getCourses() {
    return new Promise(resolve => {
        db.all("SELECT * FROM courses LIMIT 5", [], (err, rows) => {
            if (err || !rows.length) return resolve({ type: 'text', text: '目前沒有課表' });
            let msg = "📅 課表\n\n";
            rows.forEach(r => msg += `🕒 ${r.time} ${r.name}\n`);
            resolve({ type: 'text', text: msg });
        });
    });
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