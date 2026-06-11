#!/usr/bin/env python3
"""
Seed real campus data for 東吳大學 LINE Bot
Run: python seed_data.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'university_bot.db')

RESTAURANTS = [
    # 外雙溪校區 (雙溪)
    {"name": "餐憶食堂", "type": "學生餐廳", "building": "綜合大樓 B1", "business_hours": "平日 07:00-20:00", "rating": 4.2, "popular_dish": "多國美食 / 麥當勞 / 路易莎咖啡 / 7-11"},
    {"name": "蒲家廚房", "type": "小吃", "building": "學生餐廳區", "business_hours": "平日 11:00-19:00", "rating": 4.5, "popular_dish": "飯類、鍋燒意麵"},
    {"name": "金鶴餃舍", "type": "小吃", "building": "學生餐廳區", "business_hours": "平日 10:30-20:00", "rating": 4.3, "popular_dish": "麻辣鴨血麵、餃子"},
    {"name": "丼步喱", "type": "日式", "building": "學生餐廳區", "business_hours": "平日 11:00-19:30", "rating": 4.1, "popular_dish": "手作日式丼飯、咖哩"},
    {"name": "校車咖啡", "type": "咖啡輕食", "building": "校車聚場附近", "business_hours": "平日 08:00-17:00", "rating": 4.0, "popular_dish": "咖啡、輕食"},
    {"name": "萊茵咖啡坊", "type": "咖啡廳", "building": "校園內", "business_hours": "依營業公告", "rating": 4.4, "popular_dish": "精品咖啡、甜點"},
    {"name": "7-ELEVEN (餐憶)", "type": "便利商店", "building": "綜合大樓B1", "business_hours": "24小時", "rating": 3.8, "popular_dish": "御飯糰、咖啡、便當"},
    {"name": "麥當勞 (餐憶)", "type": "速食", "building": "綜合大樓B1", "business_hours": "平日 07:00-22:00", "rating": 3.9, "popular_dish": "大麥克、薯條"},
    # 城中校區
    {"name": "據德食堂", "type": "學生餐廳", "building": "第六大樓 1-3F", "business_hours": "平日 07:30-19:30", "rating": 4.0, "popular_dish": "精選美食、多樣選擇"},
]

BUS_ROUTES = [
    # Direct to campus
    {"route": "557", "name": "557 東吳大學線", "stops": "東吳大學站（外雙溪校區直達）", "note": "捷運士林站轉乘方便"},
    {"route": "紅30", "name": "紅30", "stops": "東吳大學_錢穆故居站", "note": "士林站、中正路"},
    {"route": "255", "name": "255", "stops": "東吳大學_錢穆故居站", "note": "士林捷運轉乘"},
    {"route": "300", "name": "300", "stops": "東吳大學 / 錢穆故居", "note": "多站可達"},
    {"route": "304", "name": "304", "stops": "東吳大學_錢穆故居站", "note": ""},
    {"route": "681", "name": "681", "stops": "東吳大學_錢穆故居站", "note": "文湖線劍南路轉乘"},
    {"route": "680", "name": "680", "stops": "東吳大學_錢穆故居站", "note": ""},
    {"route": "683", "name": "683", "stops": "東吳大學_錢穆故居站", "note": "淡水線士林轉"},
    {"route": "957", "name": "957", "stops": "東吳大學_錢穆故居站", "note": ""},
    {"route": "棕13", "name": "棕13", "stops": "外雙溪_故宮站", "note": "故宮博物院附近，下車步行或轉"},
    {"route": "棕20", "name": "棕20", "stops": "外雙溪_故宮站", "note": "文湖線大直/劍南路轉"},
    {"route": "校車", "name": "東吳大學校車", "stops": "外雙溪 ↔ 城中校區", "note": "上課日行駛，詳見官網或公告"},
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ensure restaurants table exists (it does from previous)
    c.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            building TEXT,
            business_hours TEXT,
            rating REAL DEFAULT 0,
            popular_dish TEXT
        )
    """)

    # Clear and reseed restaurants
    c.execute("DELETE FROM restaurants")
    for r in RESTAURANTS:
        c.execute("""
            INSERT INTO restaurants (name, type, building, business_hours, rating, popular_dish)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (r["name"], r["type"], r["building"], r["business_hours"], r["rating"], r["popular_dish"]))

    # Buses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT NOT NULL,
            name TEXT,
            stops TEXT,
            note TEXT
        )
    """)
    c.execute("DELETE FROM buses")
    for b in BUS_ROUTES:
        c.execute("""
            INSERT INTO buses (route, name, stops, note)
            VALUES (?, ?, ?, ?)
        """, (b["route"], b["name"], b["stops"], b["note"]))

    conn.commit()
    print(f"✅ Seeded {len(RESTAURANTS)} restaurants and {len(BUS_ROUTES)} bus routes.")
    print(f"📍 DB: {DB_PATH}")
    conn.close()

if __name__ == "__main__":
    seed()
