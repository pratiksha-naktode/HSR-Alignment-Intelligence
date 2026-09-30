import sqlite3

db = r"data\processed\MxlAiN_styles.db"

con = sqlite3.connect(db)

rows = con.execute("""
    SELECT id, name
    FROM symbol
    WHERE lower(name) LIKE '%forest%'
       OR lower(name) LIKE '%agri%'
       OR lower(name) LIKE '%built%'
       OR lower(name) LIKE '%urban%'
       OR lower(name) LIKE '%crop%'
""").fetchall()

print("Matching symbols:")
for row in rows:
    print(row)

print("\nTotal:", len(rows))

con.close()