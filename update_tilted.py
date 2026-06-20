import sys, os, base64, duckdb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'attachment', '틸티드_그립.webp')
ext = os.path.splitext(img_path)[1].lower().lstrip('.')
mime = {'webp': 'image/webp', 'jpeg': 'image/jpeg', 'jpg': 'image/jpeg', 'png': 'image/png'}.get(ext, 'image/webp')
with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('ascii')
data_uri = f'data:{mime};base64,{b64}'

conn = duckdb.connect(r'C:\Users\user\DB_2026\GUNSMITH\GUNSMITH_DB.duckdb')
conn.execute("UPDATE ATTACHMENT SET image_data=? WHERE attachment_name='틸티드 그립'", [data_uri])
print('완료')
conn.close()
print('완료')
