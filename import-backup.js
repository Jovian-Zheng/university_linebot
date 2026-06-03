// import-backup.js
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'university_bot.db');
const backupPath = path.join(__dirname, 'backup.sql');

console.log('🔄 正在清除舊資料並重新匯入...');

const db = new sqlite3.Database(dbPath);

db.serialize(() => {
    // 強制清除所有表格的舊資料
    db.run(`DELETE FROM assignments`);
    db.run(`DELETE FROM courses`);
    db.run(`DELETE FROM restaurants`);
    db.run(`DELETE FROM class_schedule`);
    db.run(`DELETE FROM timetable`);
    db.run(`DELETE FROM users`);

    console.log('🧹 已清除所有舊資料');
});

fs.readFile(backupPath, 'utf8', (err, sqlContent) => {
    if (err) {
        console.error('❌ 讀取 backup.sql 失敗:', err.message);
        db.close();
        return;
    }

    db.exec(sqlContent, (err) => {
        if (err) {
            console.error('❌ 匯入失敗:', err.message);
        } else {
            console.log('✅ 資料已成功匯入！');
            console.log('🎉 現在應該沒有亂碼和重複問題了');
        }
        db.close();
    });
});