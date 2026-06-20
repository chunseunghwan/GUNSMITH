import duckdb
conn = duckdb.connect(r'C:\Users\user\DB_2026\GUNSMITH\GUNSMITH_DB.duckdb', read_only=True)
rows = conn.execute("SELECT attachment_name, length(image_data) as len FROM ATTACHMENT LIMIT 5").fetchall()
for r in rows:
    print(r)
conn.close()
