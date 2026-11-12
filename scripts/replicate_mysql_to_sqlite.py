import pymysql
import sqlite3
import os

print("="*70)
print("REPLICATING COMPLETE INSTITUTIONAL DATABASE FROM MYSQL -> SQLITE")
print("="*70)

mysql_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='camps_db',
    port=3306,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

sqlite_path = os.path.abspath('backend/camps_smart_college.db')
print(f"[*] Source MySQL: camps_db@localhost:3306")
print(f"[*] Target SQLite: {sqlite_path}")

sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_cur = sqlite_conn.cursor()

# Order of tables for foreign key integrity
tables = [
    'departments',
    'users',
    'classes',
    'subjects',
    'teachers',
    'parents',
    'students',
    'parent_students',
    'teacher_classes',
    'marks',
    'attendance',
    'semester_results',
    'model_runs',
    'predictions',
    'explanations',
    'alerts',
    'notifications',
    'remarks'
]

with mysql_conn.cursor() as mysql_cur:
    # Disable foreign keys in SQLite during bulk sync
    sqlite_cur.execute("PRAGMA foreign_keys = OFF;")
    
    for table in tables:
        try:
            mysql_cur.execute(f"SELECT * FROM {table}")
            rows = mysql_cur.fetchall()
            
            # Clear SQLite table
            sqlite_cur.execute(f"DELETE FROM {table}")
            
            if not rows:
                print(f"  [SYNC] {table:<20} -> 0 rows (table empty)")
                continue
                
            cols = list(rows[0].keys())
            placeholders = ", ".join(["?"] * len(cols))
            col_names = ", ".join([f'"{c}"' for c in cols])
            insert_sql = f'INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})'
            
            values = []
            for r in rows:
                row_vals = []
                for c in cols:
                    val = r[c]
                    # Handle boolean / tinyint or datetime or Decimal or None
                    if hasattr(val, 'isoformat'):
                        row_vals.append(val.strftime('%Y-%m-%d %H:%M:%S'))
                    elif hasattr(val, 'as_tuple'):  # decimal.Decimal
                        row_vals.append(float(val))
                    elif isinstance(val, (dict, list)):
                        import json
                        row_vals.append(json.dumps(val))
                    else:
                        row_vals.append(val)
                values.append(tuple(row_vals))
                
            sqlite_cur.executemany(insert_sql, values)
            sqlite_conn.commit()
            print(f"  [SYNC] {table:<20} -> {len(rows):<5} rows copied successfully")
        except Exception as e:
            print(f"  [ERROR] {table}: {e}")
            
    sqlite_cur.execute("PRAGMA foreign_keys = ON;")
    sqlite_conn.commit()

sqlite_conn.close()
mysql_conn.close()

print("\n" + "="*70)
print("VERIFYING SQLITE TARGET DATABASE")
print("="*70)
con2 = sqlite3.connect(sqlite_path)
c2 = con2.cursor()
for t in ['users', 'students', 'classes', 'marks', 'predictions']:
    c2.execute(f"SELECT count(*) FROM {t}")
    print(f"  * SQLite {t:<15}: {c2.fetchone()[0]}")

c2.execute("SELECT user_id, username, email, role FROM users WHERE username = '4PM23CS071'")
print(f"  * User 4PM23CS071 in SQLite: {c2.fetchone()}")
c2.execute("SELECT student_id, name, usn FROM students WHERE usn = '4PM23CS071'")
print(f"  * Student 4PM23CS071 in SQLite: {c2.fetchone()}")
con2.close()
print("="*70)
