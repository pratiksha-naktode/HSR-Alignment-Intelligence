import sqlite3

db = r".\qgz_extract\MxlAiN_styles.db"

conn = sqlite3.connect(db)

rows = conn.execute("SELECT id, name FROM symbol ORDER BY id").fetchall()

print("SYMBOLS:")
for row in rows:
    print(row)

conn.close()
