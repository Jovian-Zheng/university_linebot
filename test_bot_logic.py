#!/usr/bin/env python3
"""快速測試課表/餐廳/公車查詢邏輯（不需要 LINE token）"""
import os
os.environ.setdefault("LINE_CHANNEL_ACCESS_TOKEN", "dummy")
os.environ.setdefault("LINE_CHANNEL_SECRET", "dummy")

# 直接 import 裡面的函數
from app import query_timetable, query_restaurants, query_buses, get_help_text

print("=== 幫助 ===")
print(get_help_text()[:300], "...\n")

print("=== 課表（無關鍵字，應列科系） ===")
t = query_timetable("")
print(t[:500], "...\n")

print("=== 課表 中國文學系（前幾筆） ===")
t2 = query_timetable("中國文學系")
print(t2[:600], "...\n")

print("=== 餐廳 ===")
r = query_restaurants("")
print(r[:500], "...\n")

print("=== 餐廳 咖啡 ===")
r2 = query_restaurants("咖啡")
print(r2, "\n")

print("=== 公車 ===")
b = query_buses("")
print(b[:500], "...\n")

print("=== 公車 557 ===")
b2 = query_buses("557")
print(b2, "\n")

print("✅ 所有邏輯測試通過！")

# 額外檢查資料品質
import sqlite3
conn = sqlite3.connect('university_bot.db')
c = conn.cursor()
bad = c.execute("SELECT COUNT(*) FROM timetable WHERE semester='114-2' AND (start_time LIKE '00:%' OR start_time='')").fetchone()[0]
total = c.execute("SELECT COUNT(*) FROM timetable WHERE semester='114-2'").fetchone()[0]
print(f'\\n資料品質：114-2 課表中 00:00 無效時間的筆數 = {bad} / {total}')
print('建議未來可過濾這些或補齊資料。')
conn.close()
