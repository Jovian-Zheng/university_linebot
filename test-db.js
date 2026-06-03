// test-db.js
const db = require('./db');

console.log('🔍 正在確認資料庫內容...\n');

db.allAsync("SELECT name FROM sqlite_master WHERE type='table'")
    .then(tables => {
        console.log('📋 目前有的表格：');
        tables.forEach(t => console.log(`   ✅ ${t.name}`));

        return db.allAsync("SELECT COUNT(*) as count FROM assignments");
    })
    .then(res => {
        console.log(`\n📚 assignments 表格共有 ${res[0].count} 筆資料（應該接近 23 筆）`);
        
        return db.allAsync("SELECT * FROM assignments ORDER BY due_date LIMIT 5");
    })
    .then(rows => {
        console.log('\n📝 前 5 筆作業預覽：');
        console.table(rows);
    })
    .catch(err => {
        console.error('❌ 錯誤：', err.message);
    });