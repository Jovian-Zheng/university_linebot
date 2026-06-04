const db = require('./db');

async function main() {
    const ds = await db.allAsync(
        "SELECT COUNT(*) AS c FROM timetable WHERE semester = '114-2' AND department = '資料科學系'"
    );
    console.log('資料科學系筆數:', ds[0].c);
    const all = await db.allAsync(
        "SELECT department, COUNT(*) AS cnt FROM timetable WHERE semester = '114-2' GROUP BY department ORDER BY department"
    );
    console.log('科系總數:', all.length);
    const has = all.some((d) => d.department === '資料科學系');
    console.log('含資料科學系:', has);
}

main().catch(console.error);