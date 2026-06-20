"""증빙 이미지 생성 스크립트"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['PYTHONIOENCODING'] = 'utf-8'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import platform

# 한글 폰트 설정
if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
    if os.path.exists(font_path):
        font_manager.fontManager.addfont(font_path)
        matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

OUT = r'C:\Users\user\DB_2026\GUNSMITH\docs'

# ── 1. JOIN 쿼리 출력 이미지 ───────────────────────────────────
from database import Database
db = Database()

df = db.q("""
    SELECT w.weapon_name AS 총기명, a.slot_type AS 슬롯, a.attachment_name AS 파츠명,
           c.control_recoil_vertical   AS 수직반동,
           c.control_recoil_horizontal AS 좌우반동,
           c.control_muzzle_rise       AS 총구들림
    FROM WEAPON w
    JOIN WEAPON_ATTACHMENT_COMPAT c ON w.weapon_id = c.weapon_id
    JOIN ATTACHMENT a               ON c.attachment_id = a.attachment_id
    WHERE w.weapon_name = 'M416'
    ORDER BY a.slot_type, a.attachment_name
""")

fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.axis('off')

ax.text(0.5, 0.97,
        "3-Table JOIN: WEAPON ⋈ WEAPON_ATTACHMENT_COMPAT ⋈ ATTACHMENT",
        color='#4fc3f7', fontsize=13, fontweight='bold',
        ha='center', va='top', transform=ax.transAxes)
ax.text(0.5, 0.93,
        "WHERE w.weapon_name = 'M416'  |  총 22개 행",
        color='#6b7585', fontsize=9, ha='center', va='top', transform=ax.transAxes)

cols = ['총기명', '슬롯', '파츠명', '수직반동', '좌우반동', '총구들림']
col_widths = [0.10, 0.12, 0.30, 0.13, 0.13, 0.13]
col_x = [0.02]
for w in col_widths[:-1]:
    col_x.append(col_x[-1] + w)

# 헤더
for i, (col, x) in enumerate(zip(cols, col_x)):
    ax.text(x, 0.88, col, color='#4fc3f7', fontsize=9, fontweight='bold',
            va='top', transform=ax.transAxes)

ax.plot([0.01, 0.99], [0.865, 0.865], color='#4fc3f7', linewidth=1,
        transform=ax.transAxes)

slot_colors = {
    'Grip': '#66BB6A', 'Magazine': '#ff9800', 'Muzzle': '#4fc3f7',
    'Scope': '#e91e63', 'Stock': '#FFD700',
}

row_h = 0.82 / len(df)
for ri, (_, row) in enumerate(df.iterrows()):
    y = 0.85 - (ri + 1) * row_h
    bg = '#1e2535' if ri % 2 == 0 else '#161b27'
    rect = mpatches.FancyBboxPatch((0.01, y - row_h*0.1), 0.98, row_h*0.9,
                                    boxstyle='round,pad=0.002',
                                    facecolor=bg, edgecolor='none',
                                    transform=ax.transAxes)
    ax.add_patch(rect)

    vals = [row['총기명'], row['슬롯'], row['파츠명'],
            f"{row['수직반동']:.2f}", f"{row['좌우반동']:.2f}", f"{row['총구들림']:.2f}"]
    sc = slot_colors.get(row['슬롯'], '#dde3ed')
    colors = ['#dde3ed', sc, '#dde3ed', '#ff5252' if float(row['수직반동']) > 0 else '#66BB6A',
              '#ff5252' if float(row['좌우반동']) > 0 else '#66BB6A',
              '#ff5252' if float(row['총구들림']) > 0 else '#66BB6A']
    # 0이면 회색
    for ci, (val, color, x) in enumerate(zip(vals, colors, col_x)):
        if ci >= 3 and val == '0.00':
            color = '#6b7585'
        ax.text(x, y + row_h * 0.45, val, color=color, fontsize=8,
                va='center', transform=ax.transAxes)

plt.tight_layout(pad=0.2)
out1 = os.path.join(OUT, 'img_join_output.png')
plt.savefig(out1, dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('saved:', out1)

# ── 2. db_init.py base64 코드 스니펫 이미지 ──────────────────────
code_lines = [
    ("# WEAPON 테이블 DDL (image_data TEXT 컬럼)", '#6b7585'),
    ("CREATE TABLE IF NOT EXISTS WEAPON (", '#dde3ed'),
    ("    weapon_id    INTEGER PRIMARY KEY,", '#dde3ed'),
    ("    weapon_name  VARCHAR(50) NOT NULL,", '#dde3ed'),
    ("    ...", '#6b7585'),
    ("    image_data   TEXT,    -- base64 data URI", '#66BB6A'),
    (");", '#dde3ed'),
    ("", '#dde3ed'),
    ("# base64 변환 함수", '#6b7585'),
    ("def _to_base64(path: str) -> str:", '#4fc3f7'),
    ("    ext  = os.path.splitext(path)[1].lower().lstrip('.')", '#dde3ed'),
    ("    mime = {'webp':'image/webp','png':'image/png',...}", '#dde3ed'),
    ("    with open(path, 'rb') as f:", '#dde3ed'),
    ("        b64 = base64.b64encode(f.read()).decode('ascii')", '#dde3ed'),
    ("    return f'data:{mime};base64,{b64}'", '#FFD700'),
    ("", '#dde3ed'),
    ("# INSERT 시 사용 예시", '#6b7585'),
    ("db.run('INSERT INTO WEAPON (..., image_data) VALUES (?,?,?)',", '#dde3ed'),
    ("       [..., _to_base64(img_path)])", '#ff9800'),
]

fig2, ax2 = plt.subplots(figsize=(12, 7))
fig2.patch.set_facecolor('#0d1117')
ax2.set_facecolor('#161b27')
ax2.axis('off')

ax2.text(0.5, 0.97, "DuckDB image_data (base64) 저장 코드  —  db_init.py",
         color='#4fc3f7', fontsize=12, fontweight='bold',
         ha='center', va='top', transform=ax2.transAxes)

lh = 0.85 / len(code_lines)
for i, (line, color) in enumerate(code_lines):
    y = 0.92 - i * lh
    ax2.text(0.02, y, line, color=color, fontsize=9,
             va='top', transform=ax2.transAxes, fontfamily='monospace')

plt.tight_layout(pad=0.2)
out2 = os.path.join(OUT, 'img_code_base64.png')
plt.savefig(out2, dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('saved:', out2)

# ── 3. DB 테이블 구조 요약 이미지 ─────────────────────────────────
tables = [
    ('WEAPON', ['weapon_id PK', 'weapon_name', 'gun_type', 'bullet_type', 'damage', 'bullet_speed', 'fire_speed', 'description', 'is_custom', 'image_data TEXT']),
    ('WEAPON_RECOIL', ['recoil_id PK', 'weapon_id FK', 'recoil_vertical', 'recoil_horizontal', 'first_recoil', 'muzzle_rise', 'muzzle_shake', 'recovery_recoil', 'stability_score', 'stability_grade']),
    ('ATTACHMENT', ['attachment_id PK', 'attachment_name', 'slot_type', 'image_data TEXT', 'control_recoil_vertical', 'control_recoil_horizontal', 'control_muzzle_rise', 'control_muzzle_shake', 'mod_recovery_recoil', 'control_first_recoil']),
    ('WEAPON_ATTACHMENT_COMPAT', ['compat_id PK', 'weapon_id FK', 'attachment_id FK', 'control_recoil_vertical', 'control_recoil_horizontal', 'control_muzzle_rise', 'control_muzzle_shake', 'mod_recovery_recoil', 'control_first_recoil']),
    ('CUSTOM_CONFIG', ['config_id PK', 'weapon_id FK', 'custom_name', 'muzzle_id FK', 'stock_id FK', 'grip_id FK', 'magazine_id FK', 'scope_id FK', 'foregrip_id FK', 'created_at']),
    ('RECOIL_RESULT', ['result_id PK', 'config_id FK', 'final_recoil_vertical', 'final_recoil_horizontal', 'final_muzzle_rise', 'final_muzzle_shake', 'final_first_shot_recoil', 'final_recoil_recovery', 'stability_score', 'stability_grade']),
]

fig3, axes = plt.subplots(2, 3, figsize=(16, 10))
fig3.patch.set_facecolor('#0d1117')
fig3.suptitle('GUNSMITH DuckDB 테이블 구조  (6개 테이블)', color='#4fc3f7', fontsize=14, fontweight='bold', y=0.98)

for ax3, (tname, cols) in zip(axes.flat, tables):
    ax3.set_facecolor('#161b27')
    ax3.axis('off')
    ax3.set_title(tname, color='#4fc3f7', fontsize=10, fontweight='bold', pad=4)
    for i, col in enumerate(cols):
        color = '#FFD700' if 'PK' in col else '#ff9800' if 'FK' in col else '#66BB6A' if 'TEXT' in col else '#dde3ed'
        ax3.text(0.05, 0.92 - i * 0.09, col, color=color, fontsize=8,
                 va='top', transform=ax3.transAxes, fontfamily='monospace')

plt.tight_layout(rect=[0, 0, 1, 0.96])
out3 = os.path.join(OUT, 'img_tables.png')
plt.savefig(out3, dpi=150, bbox_inches='tight', facecolor='#0d1117')
plt.close()
print('saved:', out3)

print('\n모든 이미지 생성 완료')
