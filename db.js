// db.js
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'university_bot.db');

console.log('📍 資料庫路徑：', dbPath);

const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('❌ 資料庫連接失敗:', err.message);
    } else {
        console.log('✅ 成功連接資料庫');
    }
});

// 關鍵：把原始 all 方法包裝成 Async 版本
db.allAsync = function(sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

module.exports = db;