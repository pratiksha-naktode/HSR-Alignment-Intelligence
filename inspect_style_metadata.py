import sqlite3

db = r"data\processed\MxlAiN_styles.db"

con = sqlite3.connect(db)

print("stylemetadata columns:")
for row in con.execute("PRAGMA table_info(stylemetadata)"):
    print(row)

print("\nstylemetadata rows:")
for row in con.execute("SELECT * FROM stylemetadata"):
    print(row)

con.close()