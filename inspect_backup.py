import sqlite3

conn = sqlite3.connect('db_dev_backup_2026-02-13 (1).sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
for t in tables:
    name = t[0]
    count = cursor.execute(f'SELECT COUNT(*) FROM [{name}]').fetchone()[0]
    print(f'{name}: {count} rows')
conn.close()
