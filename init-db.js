// init-db.js
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'university_bot.db');
const db = new sqlite3.Database(dbPath);

console.log('🔄 準備讓 backup.sql 自己建立表格...');

db.serialize(() => {
    // 只刪除舊表格，不建立新表格
    db.run(`DROP TABLE IF EXISTS assignments`);
    db.run(`DROP TABLE IF EXISTS courses`);
    db.run(`DROP TABLE IF EXISTS restaurants`);
    db.run(`DROP TABLE IF EXISTS class_schedule`);
    db.run(`DROP TABLE IF EXISTS timetable`);
    db.run(`DROP TABLE IF EXISTS users`);

    console.log('✅ 舊表格已清除，準備匯入...');
});

db.close();