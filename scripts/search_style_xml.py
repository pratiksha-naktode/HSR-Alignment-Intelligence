import sqlite3

db = r"data\processed\MxlAiN_styles.db"

con = sqlite3.connect(db)

rows = con.execute("""
    SELECT name
    FROM symbol
    WHERE xml LIKE '%Forest%'
       OR xml LIKE '%Agriculture%'
       OR xml LIKE '%Built%'
       OR xml LIKE '%Urban%'
       OR xml LIKE '%Crop%'
""").fetchall()

print("Matches:")
for row in rows:
    print(row[0])

print("Total:", len(rows))

con.close()