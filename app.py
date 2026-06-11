#!/usr/bin/env python3
"""
東吳大學 LINE Bot (Python)

兩種使用方式：
1. 本地聊天模式（推薦現在用這個）：
   python local_chat.py
   → 純 Hugging Face + 校園資料，零設定，無需 ngrok、無需 LINE token

2. 完整 LINE Bot（之後要接真實 LINE 再用）：
   需要 LINE token + 公開 webhook（可以用 cloudflared 或部署到 Render 等平台，取代 ngrok）

功能：精準查課表/餐廳/公車 + Hugging Face AI 智能回答
"""
import os
import sqlite3
from datetime import datetime
import threading

from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent
)

load_dotenv()

# LINE
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Hugging Face（本地聊天模式的主要 AI）
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("❌ 缺少 LINE token！")
    print("   這個 app.py 是給真實 LINE Bot 使用的 webhook 伺服器。")
    print("   請在 .env 設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET")
    print("   （從 LINE Developers Console 的 Messaging API 取得）")
    print("")
    print("💡 想先測試 AI 與資料邏輯？請改用：")
    print("   python local_chat.py   （純本地，不需要任何 token 和公開網址）")
    exit(1)  # 避免啟動不完整的 webhook

if not HF_TOKEN:
    print("⚠️  HUGGINGFACE_API_TOKEN 未設定 → 一般問題會無法使用 AI 智能回答")
    print("   精準指令（課表 / 餐廳 / 公車）仍然正常運作")
    print("   建議去 https://huggingface.co/settings/tokens 取得免費 token")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None
handler = WebhookHandler(LINE_CHANNEL_SECRET) if LINE_CHANNEL_SECRET else None

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "university_bot.db")

WEEKDAY_MAP = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日", 0: "日"}

# ---------------- DB helpers ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_timetable(keyword: str = ""):
    """回傳課表文字 + 筆數。支援系所、班級關鍵字"""
    conn = get_db()
    cur = conn.cursor()

    base_sql = """
        SELECT course_code, course_name, teacher, class_name, department,
               day_of_week, start_time, end_time, classroom, semester
        FROM timetable
        WHERE semester = '114-2'
    """
    params = []
    title = "114-2 課表"

    kw = (keyword or "").strip()

    if not kw:
        # 列出可查系所（只算有正常上課時間的）
        rows = cur.execute("""
            SELECT department, COUNT(*) as cnt
            FROM timetable
            WHERE semester = '114-2' AND start_time NOT LIKE '00:%'
            GROUP BY department
            ORDER BY department
        """).fetchall()
        conn.close()
        if not rows:
            return "目前資料庫沒有 114-2 課表資料。"
        msg = "📋 114-2 可查詢科系（共 {} 個）\n\n".format(len(rows))
        for r in rows[:30]:
            msg += f"• {r['department']}（{r['cnt']} 門課）\n"
        msg += "\n🔎 查詢範例：\n課表 法律學系\n課表 英文一Ａ\n課表 資管"
        return msg

    # 過濾明顯無效時間（DB 中部分舊資料是 00:00）
    time_filter = " AND start_time NOT LIKE '00:%' "

    # 嘗試班級（如 中一Ａ、資科一Ａ、法律二Ｂ）
    if any(x in kw for x in ["一", "二", "三", "四", "五", "六", "Ａ", "Ｂ", "A", "B", "班"]):
        sql = base_sql + time_filter + " AND (class_name LIKE ? OR course_name LIKE ?)"
        params = [f"%{kw}%", f"%{kw}%"]
        title = kw
    else:
        # 科系關鍵字（模糊）
        sql = base_sql + time_filter + " AND (department LIKE ? OR course_name LIKE ? OR teacher LIKE ?)"
        params = [f"%{kw}%", f"%{kw}%", f"%{kw}%"]
        title = kw

    sql += " ORDER BY class_name, day_of_week, start_time LIMIT 60"
    rows = cur.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        return f"😢 找不到符合「{kw}」的 114-2 課表。\n試試「課表」看所有科系，或輸入更精確名稱如「法律學系」或「中一Ａ」。"

    lines = [f"📅 {title} 課表（114-2）\n"]
    for r in rows:
        wd = WEEKDAY_MAP.get(r["day_of_week"], "?")
        classroom = r["classroom"] or ""
        teacher = r["teacher"] or "未定"
        lines.append(f"【{r['class_name']}】{r['course_name']}")
        lines.append(f"  週{wd} {r['start_time']}-{r['end_time']} {classroom}")
        lines.append(f"  {teacher}\n")

    result = "\n".join(lines).strip()
    if len(rows) == 60:
        result += "\n（僅顯示前 60 筆，建議輸入更精確的系或班級）"
    return result

def query_restaurants(keyword: str = ""):
    conn = get_db()
    cur = conn.cursor()
    kw = (keyword or "").strip().lower()

    if kw:
        rows = cur.execute("""
            SELECT name, type, building, business_hours, rating, popular_dish
            FROM restaurants
            WHERE name LIKE ? OR type LIKE ? OR building LIKE ? OR popular_dish LIKE ?
            ORDER BY rating DESC, name
            LIMIT 12
        """, (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
    else:
        rows = cur.execute("""
            SELECT name, type, building, business_hours, rating, popular_dish
            FROM restaurants
            ORDER BY rating DESC, name
        """).fetchall()
    conn.close()

    if not rows:
        return "目前沒有符合條件的餐廳資料。"

    lines = ["🍽️ 東吳大學校園餐廳\n"]
    for r in rows:
        stars = "⭐" * int(round(r["rating"])) if r["rating"] else ""
        lines.append(f"{r['name']} {stars}")
        lines.append(f"  📍 {r['building'] or ''}")
        lines.append(f"  🕒 {r['business_hours'] or ''}")
        if r["popular_dish"]:
            lines.append(f"  🍜 {r['popular_dish']}")
        lines.append("")
    lines.append("輸入「餐廳 咖啡」或「餐廳 據德」可縮小範圍")
    return "\n".join(lines).strip()

def query_buses(keyword: str = ""):
    conn = get_db()
    cur = conn.cursor()
    kw = (keyword or "").strip()

    if kw:
        rows = cur.execute("""
            SELECT route, name, stops, note
            FROM buses
            WHERE route LIKE ? OR name LIKE ? OR stops LIKE ? OR note LIKE ?
            ORDER BY route
            LIMIT 15
        """, (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
    else:
        rows = cur.execute("SELECT route, name, stops, note FROM buses ORDER BY route").fetchall()
    conn.close()

    if not rows:
        return "找不到符合的公車路線。"

    lines = ["🚌 東吳大學周邊公車 / 交通\n"]
    for b in rows:
        lines.append(f"【{b['route']}】 {b['name']}")
        if b["stops"]:
            lines.append(f"   站牌：{b['stops']}")
        if b["note"]:
            lines.append(f"   備註：{b['note']}")
        lines.append("")
    lines.append("💡 提示：輸入「公車 557」或「公車 士林」查特定路線")
    lines.append("更多即時資訊可參考：台北市公車即時動態或 TDX 開放資料")
    return "\n".join(lines).strip()

# ====================== Hugging Face AI (for general questions) ======================

import requests as _requests

def call_huggingface(user_msg: str, context: str = "") -> str:
    """跟 local_chat.py 一致的高品質 HF 呼叫（東吳大學專屬助理）"""
    if not HF_TOKEN:
        return "（AI 功能未開啟）精準指令（課表 / 餐廳 / 公車）仍然可用。"

    system = (
        "你是「東吳大學生活小幫手」，用親切、實用、繁體中文回答東吳大學（外雙溪 / 城中校區）學生的問題。"
        "回答要簡潔清楚。如果有提供校園資料，請優先使用那些資料，不要亂編。"
        "不知道的事情就誠實說可以再查官方網站。"
    )

    prompt = f"{system}\n\n"
    if context:
        prompt += f"【校園最新資料】\n{context}\n\n"
    prompt += f"學生問：{user_msg}\n\n小幫手："

    try:
        resp = _requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 350,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "return_full_text": False,
                    "repetition_penalty": 1.1
                }
            },
            timeout=25
        )
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and data and "generated_text" in data[0]:
            text = data[0]["generated_text"]
        elif isinstance(data, dict) and "generated_text" in data:
            text = data["generated_text"]
        else:
            text = str(data)

        text = text.strip()
        if "小幫手：" in text:
            text = text.split("小幫手：", 1)[-1].strip()

        return text[:900] if len(text) > 950 else text or "（AI 沒有回覆）"
    except Exception as e:
        return f"AI 目前忙線中，請稍後再試或直接用「課表」「餐廳」等指令。"

def get_university_context(query: str):
    """自動為 AI 準備相關校園資料（跟 local_chat.py 同步）"""
    q = (query or "").lower()
    context = []

    if any(k in query for k in ["課表", "上課", "課程", "系", "班"]):
        conn = get_db()
        depts = conn.execute("""
            SELECT department FROM timetable 
            WHERE semester='114-2' AND start_time NOT LIKE '00:%'
            GROUP BY department ORDER BY COUNT(*) DESC LIMIT 8
        """).fetchall()
        conn.close()
        context.append("目前有資料的科系（部分）： " + "、".join([d[0] for d in depts]))

    if any(k in q for k in ["餐廳", "吃", "美食", "午餐", "晚餐", "咖啡", "食堂"]):
        conn = get_db()
        rests = conn.execute("SELECT name, building, popular_dish FROM restaurants ORDER BY rating DESC LIMIT 5").fetchall()
        conn.close()
        context.append("校園餐廳推薦：" + "；".join([f"{r['name']}({r['building']})" for r in rests]))

    if any(k in q for k in ["公車", "交通", "怎麼去", "站牌", "校車", "士林", "故宮"]):
        conn = get_db()
        buses = conn.execute("SELECT route, name, stops FROM buses LIMIT 6").fetchall()
        conn.close()
        context.append("常見公車：" + "、".join([f"{b['route']}({b['stops']})" for b in buses]))

    return "\n".join(context) if context else ""

def get_help_text():
    return (
        "👋 歡迎使用東吳大學生活小幫手！\n\n"
        "📚 查課表\n"
        "   直接輸入「課表」看所有科系\n"
        "   「課表 法律學系」或「課表 中一Ａ」\n\n"
        "🍽️ 看餐廳\n"
        "   「餐廳」或「吃什麼」列出校園餐廳\n"
        "   「餐廳 咖啡」「餐廳 據德」搜尋\n\n"
        "🚌 看公車 / 交通\n"
        "   「公車」列出常見路線\n"
        "   「公車 557」「公車 士林」\n\n"
        "❓ 其他\n"
        "   「幫助」顯示本訊息\n\n"
        "💡 小提醒：課表資料為 114-2 學期，實際以學校系統為準。\n"
        "官方課表查詢：https://web.sys.scu.edu.tw/class40.asp?option=1"
    )

# ---------------- Quick Reply helper ----------------
def make_main_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="📚 課表", text="課表")),
        QuickReplyButton(action=MessageAction(label="🍽️ 餐廳", text="餐廳")),
        QuickReplyButton(action=MessageAction(label="🚌 公車", text="公車")),
        QuickReplyButton(action=MessageAction(label="❓ 幫助", text="幫助")),
    ])

# ---------------- Message handler ----------------
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if line_bot_api is None:
        return

    text = (event.message.text or "").strip()
    reply_token = event.reply_token
    lower = text.lower()

    print(f"[LINE] 收到: {text}")

    reply_text = None
    quick_reply = make_main_quick_reply()

    # 優先處理關鍵字
    if any(k in text for k in ["幫助", "help", "指令", "怎麼用", "menu", "選單"]):
        reply_text = get_help_text()

    elif "課表" in text:
        # 去掉「課表」後的剩餘當關鍵字
        rest = text.replace("課表", "", 1).strip()
        reply_text = query_timetable(rest)

    elif any(k in text for k in ["餐廳", "吃什麼", "美食", "午餐", "晚餐", "cafeteria"]):
        rest = text
        for k in ["餐廳", "吃什麼", "美食"]:
            rest = rest.replace(k, "", 1).strip()
        reply_text = query_restaurants(rest)

    elif any(k in text for k in ["公車", "bus", "交通", "怎麼去", "站牌", "校車"]):
        rest = text
        for k in ["公車", "bus", "交通"]:
            rest = rest.replace(k, "", 1).strip()
        reply_text = query_buses(rest)

    elif any(k in lower for k in ["hi", "hello", "你好", "嗨"]):
        reply_text = "你好！我是東吳大學小幫手 😊\n輸入「幫助」看功能，或直接按下方按鈕試試～"

    else:
        # 沒有匹配精準指令 → 交給 Hugging Face AI（會自動帶校園資料）
        context = get_university_context(text)
        reply_text = call_huggingface(text, context)

    # 安全截斷（LINE 單則文字上限約 5000 字）
    if reply_text and len(reply_text) > 4900:
        reply_text = reply_text[:4890] + "\n...（內容過長已截斷）"

    try:
        msg = TextSendMessage(text=reply_text or "收到！", quick_reply=quick_reply)
        line_bot_api.reply_message(reply_token, msg)
    except Exception as e:
        print("回覆失敗:", e)
        # 避免拋出導致 LINE 重試
        try:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="系統忙線中，請稍後再試。"))
        except:
            pass

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    【關鍵改進】 
    立即回 200 給 LINE，避免 timeout。
    實際的訊息處理（包含呼叫 Hugging Face）放到背景執行緒執行。
    這樣即使 HF 回應慢 10-20 秒，LINE 也不會把 webhook 當失敗。
    replyToken 在這段時間內仍然有效。
    """
    if handler is None:
        abort(500, "LINE handler not configured")

    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    # 立即回應 200
    # 然後背景處理
    def process_in_background():
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("❌ Invalid signature in background.")
        except Exception as e:
            print("Background processing error:", e)

    threading.Thread(target=process_in_background, daemon=True).start()
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return (
        "<h1>東吳大學 LINE Bot</h1>"
        "<p>Webhook endpoint: <code>/webhook</code></p>"
        "<p>狀態：已啟動 ✅</p>"
    )

if __name__ == "__main__":
    # HF Spaces usually uses 7860, but we respect PORT env var
    port = int(os.getenv("PORT", 7860))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print("🚀 東吳大學 LINE Bot (Hugging Face Spaces 版) 啟動中...")
    print(f"   Port: {port}")
    print(f"   Webhook endpoint: /webhook")
    print("   部署後請將完整 Space URL + /webhook 設定到 LINE Developers Console")
    app.run(host="0.0.0.0", port=port, debug=debug)
