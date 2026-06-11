#!/usr/bin/env python3
"""
東吳大學 本地聊天模式 (Hugging Face + 校園資料庫)
===========================================
你「只要 Hugging Face」就可以用這個！

特色：
- 完全本地執行，不需要 LINE token、不需要 ngrok、不需要公開網址
- 精準查詢：課表 / 餐廳 / 公車 會直接用資料庫回覆（最準）
- 一般問題、閒聊、複雜問題 → 用 Hugging Face AI 回答，並自動帶入校園資料當 context
- 直接在終端機聊天，超方便開發測試

使用方式：
  1. pip install -r requirements.txt
  2. 在 .env 填入 HUGGINGFACE_API_TOKEN（LINE token 可以不管）
  3. python local_chat.py

輸入 "exit" 或 "離開" 結束。
"""
import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
DB_PATH = os.path.join(os.path.dirname(__file__), "university_bot.db")

WEEKDAY_MAP = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日", 0: "日"}

# ====================== DB 查詢（精準工具） ======================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query_timetable(keyword: str = ""):
    """精準課表查詢"""
    conn = get_db()
    cur = conn.cursor()

    base = """
        SELECT course_name, teacher, class_name, department,
               day_of_week, start_time, end_time, classroom
        FROM timetable
        WHERE semester = '114-2' AND start_time NOT LIKE '00:%'
    """
    kw = (keyword or "").strip()

    if not kw:
        rows = cur.execute("""
            SELECT department, COUNT(*) as cnt
            FROM timetable
            WHERE semester = '114-2' AND start_time NOT LIKE '00:%'
            GROUP BY department ORDER BY department
        """).fetchall()
        conn.close()
        if not rows:
            return "目前沒有 114-2 課表資料。"
        msg = "📋 114-2 可查詢科系（共 {} 個）\n\n".format(len(rows))
        for r in rows[:25]:
            msg += f"• {r['department']}（{r['cnt']} 門）\n"
        msg += "\n範例：課表 法律學系、課表 中一Ａ、課表 資管"
        return msg

    if any(x in kw for x in ["一", "二", "三", "四", "五", "六", "Ａ", "Ｂ", "A", "B", "班"]):
        sql = base + " AND (class_name LIKE ? OR course_name LIKE ?) "
        params = [f"%{kw}%", f"%{kw}%"]
    else:
        sql = base + " AND (department LIKE ? OR course_name LIKE ? OR teacher LIKE ?) "
        params = [f"%{kw}%", f"%{kw}%", f"%{kw}%"]

    sql += " ORDER BY class_name, day_of_week, start_time LIMIT 50"
    rows = cur.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        return f"找不到「{kw}」的課表資料。試試「課表」看所有科系。"

    lines = [f"📅 課表：{kw}（114-2）\n"]
    for r in rows:
        wd = WEEKDAY_MAP.get(r["day_of_week"], "?")
        cls = r["classroom"] or ""
        tch = r["teacher"] or "未定"
        lines.append(f"【{r['class_name']}】{r['course_name']}")
        lines.append(f"  週{wd} {r['start_time']}-{r['end_time']} {cls}｜{tch}\n")
    return "\n".join(lines).strip()

def query_restaurants(keyword: str = ""):
    conn = get_db()
    cur = conn.cursor()
    kw = (keyword or "").strip()

    if kw:
        rows = cur.execute("""
            SELECT name, type, building, business_hours, rating, popular_dish
            FROM restaurants
            WHERE name LIKE ? OR type LIKE ? OR building LIKE ? OR popular_dish LIKE ?
            ORDER BY rating DESC LIMIT 10
        """, (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
    else:
        rows = cur.execute("""
            SELECT name, type, building, business_hours, rating, popular_dish
            FROM restaurants ORDER BY rating DESC
        """).fetchall()
    conn.close()

    if not rows:
        return "目前沒有符合的餐廳資料。"

    lines = ["🍽️ 東吳大學餐廳\n"]
    for r in rows:
        stars = "⭐" * int(round(r["rating"] or 0))
        lines.append(f"{r['name']} {stars}")
        lines.append(f"  📍{r['building'] or ''}  🕒{r['business_hours'] or ''}")
        if r["popular_dish"]:
            lines.append(f"  🍜 {r['popular_dish']}")
        lines.append("")
    return "\n".join(lines).strip()

def query_buses(keyword: str = ""):
    conn = get_db()
    cur = conn.cursor()
    kw = (keyword or "").strip()

    if kw:
        rows = cur.execute("""
            SELECT route, name, stops, note FROM buses
            WHERE route LIKE ? OR name LIKE ? OR stops LIKE ? OR note LIKE ?
            ORDER BY route LIMIT 12
        """, (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
    else:
        rows = cur.execute("SELECT route, name, stops, note FROM buses ORDER BY route").fetchall()
    conn.close()

    if not rows:
        return "找不到相關公車資料。"

    lines = ["🚌 東吳大學周邊公車\n"]
    for b in rows:
        lines.append(f"【{b['route']}】{b['name']}")
        if b["stops"]: lines.append(f"   站牌：{b['stops']}")
        if b["note"]:  lines.append(f"   {b['note']}")
        lines.append("")
    return "\n".join(lines).strip()

def get_university_context(query: str):
    """根據使用者問題，自動抓相關校園資料當 context 給 AI"""
    q = query.lower()
    context = []

    if any(k in query for k in ["課表", "上課", "課程", "系", "班"]):
        # 給一點系所清單
        conn = get_db()
        depts = conn.execute("""
            SELECT department, COUNT(*) as c FROM timetable 
            WHERE semester='114-2' AND start_time NOT LIKE '00:%'
            GROUP BY department ORDER BY c DESC LIMIT 8
        """).fetchall()
        conn.close()
        context.append("目前有資料的科系（部分）： " + "、".join([d["department"] for d in depts]))

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

# ====================== Hugging Face ======================

def call_huggingface(user_msg: str, context: str = "") -> str:
    if not HF_TOKEN:
        return "（目前沒有設定 HUGGINGFACE_API_TOKEN，無法使用 AI 回覆）\n請在 .env 裡加上你的 HF Token。"

    # 強力 prompt：東吳大學專屬助理
    system = (
        "你是「東吳大學生活小幫手」，用親切、實用、繁體中文回答東吳大學（外雙溪 / 城中校區）學生的問題。"
        "回答要簡潔清楚。如果有提供校園資料，請優先使用那些資料，不要亂編。"
        "不知道的事情就誠實說可以再查官方網站。"
    )

    prompt = f"{system}\n\n"
    if context:
        prompt += f"【校園最新資料】\n{context}\n\n"
    prompt += f"學生問：{user_msg}\n\n小幫手："

    # 使用 Mistral Instruct（跟你原本 JS 用的類似）
    model = "mistralai/Mistral-7B-Instruct-v0.3"
    url = f"https://api-inference.huggingface.co/models/{model}"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 350,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False,
            "repetition_penalty": 1.1
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and data and "generated_text" in data[0]:
            text = data[0]["generated_text"]
        elif isinstance(data, dict) and "generated_text" in data:
            text = data["generated_text"]
        else:
            text = str(data)

        # 清理
        text = text.strip()
        # 去掉重複的 prompt 部分
        if "小幫手：" in text:
            text = text.split("小幫手：", 1)[-1].strip()
        if len(text) > 900:
            text = text[:850] + "……（回答較長，已截斷）"

        return text or "（AI 目前沒有給出有效回覆）"
    except requests.exceptions.Timeout:
        return "AI 回應太久了，請再試一次或換個問題。"
    except Exception as e:
        return f"AI 呼叫失敗：{e}\n（請檢查 HUGGINGFACE_API_TOKEN 是否有效，或稍後再試）"

# ====================== 主聊天迴圈 ======================

def main():
    print("🎓 東吳大學本地小幫手（Hugging Face 模式）")
    print("   直接輸入問題，例如：")
    print("     課表 法律學系")
    print("     餐廳 有沒有好吃的")
    print("     公車 怎麼去士林")
    print("     外雙溪今天天氣如何？")
    print("     圖書館幾點關門？")
    print("   輸入 exit / 離開 結束\n")

    if not HF_TOKEN:
        print("⚠️  警告：.env 裡沒有找到 HUGGINGFACE_API_TOKEN")
        print("   AI 功能會無法使用，但精準查詢（課表/餐廳/公車）還是可以的。\n")

    while True:
        try:
            user_input = input("你： ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "離開", "結束", "bye"):
            print("小幫手：掰掰～有問題再來找我！")
            break

        # 1. 先看有沒有精準指令（優先用資料庫，最準確）
        text = user_input

        if "課表" in text:
            rest = text.replace("課表", "", 1).strip()
            reply = query_timetable(rest)
        elif any(k in text for k in ["餐廳", "吃什麼", "美食", "午餐", "晚餐"]):
            rest = text
            for k in ["餐廳", "吃什麼", "美食"]:
                rest = rest.replace(k, "", 1).strip()
            reply = query_restaurants(rest)
        elif any(k in text for k in ["公車", "交通", "校車", "怎麼去"]):
            rest = text
            for k in ["公車", "交通"]:
                rest = rest.replace(k, "", 1).strip()
            reply = query_buses(rest)
        elif any(k in text.lower() for k in ["幫助", "help", "指令"]):
            reply = (
                "📚 課表 + 系所/班級名稱\n"
                "🍽️ 餐廳 / 吃什麼 （可加關鍵字）\n"
                "🚌 公車 / 交通 （可加路線或地點）\n"
                "其他問題我會用 AI 幫你解答（會參考校園資料）"
            )
        else:
            # 2. 一般問題 → 抓 context + 呼叫 Hugging Face
            context = get_university_context(text)
            reply = call_huggingface(text, context)

        print(f"\n小幫手：{reply}\n")

if __name__ == "__main__":
    main()
