import sqlite3

conn = sqlite3.connect('db_dev_backup_2026-02-13 (1).sqlite3')
cursor = conn.cursor()

# Check student id_numbers that exceed PostgreSQL integer range
MAX_INT = 2147483647
cursor.execute(f"SELECT student_id, name, lastname, id_number FROM students_student WHERE id_number > {MAX_INT} OR id_number < -{MAX_INT}")
rows = cursor.fetchall()
print(f"Students with id_number exceeding PostgreSQL integer range ({MAX_INT}):")
print(f"Found {len(rows)} problematic records")
for r in rows:
    print(f"  PK={r[0]}, Name={r[1]} {r[2]}, id_number={r[3]}")

# Also check all integer fields across all tables for overflow
print("\n--- Checking all tables for large integers ---")
tables_to_check = [
    ("students_student", "id_number"),
    ("students_student", "student_id"),
]
for table, col in tables_to_check:
    cursor.execute(f"SELECT MAX({col}), MIN({col}) FROM {table}")
    row = cursor.fetchone()
    print(f"  {table}.{col}: MIN={row[1]}, MAX={row[0]}")

conn.close()
