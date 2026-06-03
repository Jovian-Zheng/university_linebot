--
-- File generated with SQLiteStudio v3.4.21 on 週二 六月 2 20:23:16 2026
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: assignments
CREATE TABLE IF NOT EXISTS "assignments" (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      course_name TEXT,
      title TEXT NOT NULL,
      type TEXT,                  -- 'homework' 或 'exam'
      due_date TEXT,              -- YYYY-MM-DD
      due_time TEXT,              -- HH:MM
      description TEXT,
      reminder_sent INTEGER DEFAULT 0
    );
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (1, '線性代數', '作業1 - 向量空間基礎', '作業', '2026-06-05', '23:59', '完成課本第1章習題 1-15', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (2, '線性代數', '作業2 - 線性轉換', '作業', '2026-06-08', '23:59', '證明線性轉換相關定理', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (3, '線性代數', '作業3 - 矩陣運算', '作業', '2026-06-12', '23:59', '計算行列式與反矩陣', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (4, '線性代數', '小考1', '考試', '2026-06-15', '10:00', '範圍：第1-3章', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (5, '線性代數', '作業4 - 特徵值與特徵向量', '作業', '2026-06-18', '23:59', '求矩陣的特徵值', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (6, '線性代數', '作業5 - 正交化', '作業', '2026-06-22', '23:59', 'Gram-Schmidt 正交化過程', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (7, '線性代數', '期中報告', '作業', '2026-06-25', '23:59', '應用線性代數於實際問題（3-5頁）', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (8, '線性代數', '作業6 - 對角化', '作業', '2026-06-29', '23:59', '判斷矩陣是否可對角化', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (9, '線性代數', '小考2', '考試', '2026-07-02', '10:00', '範圍：第4-6章', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (10, '線性代數', '期末複習作業', '作業', '2026-07-10', '23:59', '完成歷屆考題 10 題', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (11, '程式設計', '20260309_助教課練習題', '作業', '2026-03-09', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (12, '程式設計', '20260504助教課練習題', '作業', '2026-05-04', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (13, '程式設計', '20260518_助教課作業', '作業', '2026-05-18', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (14, '程式設計', 'ch15單元練習題', '作業', '2026-06-01', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (15, '程式設計', 'ch12單元練習題', '作業', '2026-06-01', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (16, '程式設計', 'ch14單元練習題', '作業', '2026-06-01', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (17, '程式設計', '20260312課堂作業', '作業', '2026-03-12', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (18, '程式設計', 'Excel AI Ally 後測考卷、問卷截圖繳交', '作業', '2026-06-01', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (19, '程式設計', '20260409_課堂練習題', '作業', '2026-04-09', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (20, '程式設計', '20260416_課堂練習題', '作業', '2026-04-16', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (21, '程式設計', '20260430_課堂練習題', '作業', '2026-04-30', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (22, '程式設計', '20260528_課堂作業', '作業', '2026-05-28', '23:59', '個人作業', 0);
INSERT INTO assignments (id, course_name, title, type, due_date, due_time, description, reminder_sent) VALUES (23, '程式設計', '個人網站開發', '作業', '2026-06-11', '23:59', '個人網站開發專案 (2026-05-28 ~ 2026-06-11)', 0);

-- Table: class_schedule
CREATE TABLE IF NOT EXISTS class_schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, class_name TEXT, grade INTEGER, day_of_week INTEGER, start_time TEXT, end_time TEXT, classroom TEXT, semester TEXT, week_type TEXT DEFAULT 'all', FOREIGN KEY (course_id) REFERENCES courses (id));
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (1, 1, '中一-A', 1, 3, '08:10', '10:00', 'B710', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (2, 2, '中一-A', 1, 5, '10:20', '12:10', 'D0731', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (3, 3, '中一-A', 1, 4, '13:30', '15:20', 'D0618', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (4, 4, '中一-A', 1, 2, '10:20', '12:10', 'R0313', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (5, 5, '中一-A', 1, 3, '10:20', '12:10', 'B710', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (6, 6, '中一-A', 1, 5, '13:30', '15:20', 'D0634', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (7, 7, '中一-A', 1, 3, '15:30', '17:20', 'D0401', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (8, 8, '中一-A', 1, 5, '08:10', '10:00', 'D0634', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (9, 9, '中一-A', 1, 1, '15:30', '17:20', '0241', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (10, 5, '中一-A', 1, 3, '10:20', '12:10', 'D0731', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (11, 11, '中一-A', 1, 4, '08:10', '10:00', 'D0731', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (12, 2, '中一-A', 1, 5, '10:20', '12:10', '待查', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (13, 13, '中一-A', 1, 3, '12:20', '13:10', '0101', '114-2', 'all');
INSERT INTO class_schedule (id, course_id, class_name, grade, day_of_week, start_time, end_time, classroom, semester, week_type) VALUES (14, 14, '中一-A', 1, 5, '15:30', '17:20', '待查', '114-2', 'all');

-- Table: courses
CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY AUTOINCREMENT, course_code TEXT, course_name TEXT NOT NULL, teacher TEXT, credits INTEGER, hours INTEGER, department TEXT, required_type TEXT DEFAULT '必修', UNIQUE (course_code, teacher));
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (1, 'BCN10101', '文學概論', '康愷霈', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (2, 'BCN10201', '國學導讀', '陳恒嵩', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (3, 'BCN11601', '孟子', '涂美雲', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (4, 'BCN14301', '現代文學史', '鍾正道', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (5, 'BCN46001', '現代散文選讀及習作', '許蓓苓', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (6, 'BCN47101', '現代戲劇及習作', '侯淑娟', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (7, 'BCN49102', '書法一技之長、篆書', '吳啟禎', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (8, 'BCN52201', '魏晉南北朝文學史', '陳愷玲', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (9, 'BDC99581', '通識課程（一）', '待查', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (10, 'BHS13901', '影視編劇—文學與電影', '鍾正道', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (11, 'BSP17101', '國文', '林盈玥', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (12, 'BSP29531', '外文（一）', '待查', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (13, 'BSP99001', '系會時間', '待查', 0, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (14, 'BSP99701', '體育', '待查', 0, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (15, 'BCN10102', '文學概論', '鍾正道', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (16, 'BCN10202', '國學導讀', '涂美雲', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (21, 'BCN52202', '魏晉南北朝文學史', '林伯謙', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (24, 'BSP17103', '國文', '嚴瑄凱', 2, NULL, NULL, '必修');
INSERT INTO courses (id, course_code, course_name, teacher, credits, hours, department, required_type) VALUES (25, 'BSP92541', '外文（一）', '待查', 2, NULL, NULL, '必修');

-- Table: restaurants
CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type TEXT, building TEXT, business_hours TEXT, rating REAL DEFAULT 0, popular_dish TEXT);

-- Table: timetable
CREATE TABLE IF NOT EXISTS timetable (
    course_code TEXT,
    course_name TEXT,
    teacher TEXT,
    credits INTEGER,
    required_type TEXT,
    class_name TEXT,
    grade INTEGER,
    department TEXT,
    day_of_week INTEGER,
    start_time TEXT,
    end_time TEXT,
    classroom TEXT,
    week_type TEXT,
    semester TEXT
);
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN10101', '文學概論', '康愷霈', 2, '必修', '中一-A', 1, '中國文學系', 3, '上午 08:10:00', '上午 10:00:00', 'B710', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN10201', '國學導讀', '陳恒嵩', 2, '必修', '中一-A', 1, '中國文學系', 5, '上午 10:20:00', '下午 12:10:00', 'D0731', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN11601', '孟子', '涂美雲', 2, '選修', '中一-A', 1, '中國文學系', 4, '下午 01:30:00', '下午 03:20:00', 'D0618', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN14301', '現代文學史', '鍾正道', 2, '必修', '中一-A', 1, '中國文學系', 2, '上午 10:20:00', '下午 12:10:00', 'R0313', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN46001', '現代散文選讀及習作', '許蓓苓', 2, '選修', '中一-A', 1, '中國文學系', 3, '上午 10:20:00', '下午 12:10:00', 'B710', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN47101', '現代戲劇及習作', '侯淑娟', 2, '選修', '中一-A', 1, '中國文學系', 5, '下午 01:30:00', '下午 03:20:00', 'D0634', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN49102', '書法一技之長、篆書', '吳啟禎', 2, '選修', '中一-A', 1, '中國文學系', 3, '下午 03:30:00', '下午 05:20:00', 'D0401', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BCN52201', '魏晉南北朝文學史', '陳愷玲', 2, '必修', '中一-A', 1, '中國文學系', 5, '上午 08:10:00', '上午 10:00:00', 'D0634', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BDC99581', '通識課程（一）', '待查', 2, '通識', '中一-A', 1, '中國文學系', 1, '下午 03:30:00', '下午 05:20:00', '0241', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BHS13901', '影視編劇—文學與電影', '鍾正道', 2, '選修', '中一-A', 1, '中國文學系', 3, '上午 10:20:00', '下午 12:10:00', 'D0731', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BSP17101', '國文', '林盈玥', 2, '必修', '中一-A', 1, '中國文學系', 4, '上午 08:10:00', '上午 10:00:00', 'D0731', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BSP29531', '外文（一）', '待查', 2, '必修', '中一-A', 1, '中國文學系', 5, '上午 10:20:00', '下午 12:10:00', '待查', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BSP99001', '系會時間', '待查', 0, '必修', '中一-A', 1, '中國文學系', 3, '下午 12:20:00', '下午 01:10:00', '0101', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('BSP99701', '體育', '待查', 0, '必修', '中一-A', 1, '中國文學系', 5, '下午 03:30:00', '下午 05:20:00', '待查', 'all', '114-2');
INSERT INTO timetable (course_code, course_name, teacher, credits, required_type, class_name, grade, department, day_of_week, start_time, end_time, classroom, week_type, semester) VALUES ('', '', '', '', '', '', '', '', '', '', '', '', '', '');

-- Table: users
CREATE TABLE IF NOT EXISTS users (
      line_user_id TEXT PRIMARY KEY,
      department TEXT,
      grade TEXT,
      name TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
