import sqlite3

conn = sqlite3.connect('university_bot.db')
c = conn.cursor()

print('TABLES:', [x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])

for tbl in ['timetable', 'restaurants', 'assignments', 'courses', 'class_schedule']:
    try:
        n = c.execute(f'SELECT COUNT(1) FROM {tbl}').fetchone()[0]
        print(f'{tbl}: {n} rows')
        if n > 0 and n < 100:
            sample = c.execute(f'SELECT * FROM {tbl} LIMIT 1').fetchone()
            print(f'  sample: {sample}')
    except Exception as e:
        print(tbl, 'ERR:', e)

print('\n--- Timetable depts (114-2) ---')
try:
    rows = c.execute("SELECT department, COUNT(*) as cnt FROM timetable WHERE semester='114-2' GROUP BY department ORDER BY cnt DESC").fetchall()
    for r in rows[:10]:
        print(r)
except Exception as e:
    print('dept err', e)

print('\n--- timetable schema ---')
print([x[1] for x in c.execute('PRAGMA table_info(timetable)')])
print('\nSample timetable rows:')
for r in c.execute("SELECT course_code, course_name, teacher, class_name, department, day_of_week, start_time, end_time, classroom, semester FROM timetable WHERE semester='114-2' LIMIT 3").fetchall():
    print(r)

print('\n--- restaurants schema ---')
print(c.execute('PRAGMA table_info(restaurants)').fetchall())

conn.close()
print('\nDone.')