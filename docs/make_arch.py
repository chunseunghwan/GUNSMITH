"""시스템 전체 구성도 생성"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import platform
from matplotlib import font_manager
import os

if platform.system() == 'Windows':
    fp = 'C:/Windows/Fonts/malgun.ttf'
    if os.path.exists(fp):
        font_manager.fontManager.addfont(fp)
        matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(18, 11))
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#f8f9fa')
ax.set_xlim(0, 18)
ax.set_ylim(0, 11)
ax.axis('off')

C_BLUE  = '#4361ee'
C_MAIN  = '#3a86ff'
C_RED   = '#e63946'
C_GREEN = '#2d6a4f'
C_TEAL  = '#2ec4b6'
C_GOLD  = '#856404'
C_BGBLUE = '#e8f0ff'
C_BGRED  = '#ffe8e8'
C_BGGREEN= '#d8f3dc'
C_BGGOLD = '#fff3cd'
C_TEXT  = '#1a1a2e'

def box(ax, x, y, w, h, fc, ec, lw=2, radius=0.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2))

def header(ax, x, y, w, h, color, title, subtitle=''):
    box(ax, x, y, w, h, color, color)
    ax.text(x+w/2, y+h*0.65, title, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white', zorder=3)
    if subtitle:
        ax.text(x+w/2, y+h*0.2, subtitle, ha='center', va='center',
                fontsize=7.5, color='#cce4ff', zorder=3)

def small_box(ax, x, y, w, h, fc, ec, text, fs=8.5, tc=C_TEXT):
    box(ax, x, y, w, h, fc, ec, lw=1, radius=0.1)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center',
            fontsize=fs, color=tc, zorder=3)

def arrow(ax, x1, y1, x2, y2, color, dash=False, rad=0.0):
    ls = (0, (5, 3)) if dash else '-'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=1.8,
                        linestyle=ls,
                        connectionstyle=f'arc3,rad={rad}'))

def alabel(ax, x, y, text, color, fs=8.5):
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=color, zorder=4)

# ── 제목 ──
ax.text(9, 10.55, 'GUNSMITH 시스템 전체 구성도', ha='center', fontsize=16,
        fontweight='bold', color=C_TEXT, zorder=4)
ax.text(9, 10.18, '※ Repository Pattern으로 DB 독립성 확보 — DuckDB / MySQL 교체 가능',
        ha='center', fontsize=9, color='#555', zorder=4)

# ════════════════════════════════
# 1. 사용자
# ════════════════════════════════
ux, uy = 0.3, 4.8
circle = plt.Circle((ux+0.5, uy+1.85), 0.38, color=C_BLUE, zorder=3)
ax.add_patch(circle)
body = mpatches.Arc((ux+0.5, uy+1.1), 0.9, 0.9, angle=0,
                     theta1=180, theta2=0, color=C_BLUE, linewidth=3, zorder=3)
ax.add_patch(body)
ax.text(ux+0.5, uy+0.35, '사용자', ha='center', fontsize=11,
        fontweight='bold', color=C_TEXT, zorder=4)
ax.text(ux+0.5, uy-0.05, 'User', ha='center', fontsize=8, color='#555', zorder=4)

# ════════════════════════════════
# 2. Flet GUI
# ════════════════════════════════
gx, gy = 2.1, 3.5
gw, gh = 2.8, 3.6
box(ax, gx, gy, gw, gh, 'white', C_BLUE, lw=2)
header(ax, gx, gy+gh-0.55, gw, 0.55, C_BLUE, 'Flet GUI')
tabs = ['총기 정보', '파츠 정보', '파츠 커스텀', '비교 분석']
for i, t in enumerate(tabs):
    r, c = divmod(i, 2)
    fc = C_BGBLUE if i == 0 else '#f0f0f0'
    small_box(ax, gx+0.1+c*1.35, gy+gh-1.15-r*0.55, 1.25, 0.42, fc, C_BLUE, t, fs=8)
small_box(ax, gx+0.1, gy+0.6,  gw-0.2, 0.38, '#f0f4ff', C_BLUE, '이미지(base64) 직접 출력', fs=8)
small_box(ax, gx+0.1, gy+0.15, gw-0.2, 0.38, '#f0f4ff', C_BLUE, '커스텀 저장 · 비교 출력', fs=8)

# ════════════════════════════════
# 3. GUNSMITH App (Service + Repository Interface)
# ════════════════════════════════
ax2, ay2 = 6.0, 2.8
aw, aah = 3.6, 4.8
box(ax, ax2, ay2, aw, aah, 'white', C_MAIN, lw=2)
header(ax, ax2, ay2+aah-0.6, aw, 0.6, C_MAIN, 'GUNSMITH App', 'Python · Repository Pattern')

# Service layer
ax.text(ax2+aw/2, ay2+aah-0.85, '[ Service Layer ]', ha='center', fontsize=8,
        color=C_MAIN, fontweight='bold', zorder=3)
svcs = ['WeaponService', 'AttachmentService', 'CustomService', 'CompareService']
for i, s in enumerate(svcs):
    small_box(ax, ax2+0.15, ay2+aah-1.35-i*0.48, aw-0.3, 0.38, C_BGBLUE, C_MAIN, s, fs=8.5)

ax.plot([ax2+0.1, ax2+aw-0.1], [ay2+2.15, ay2+2.15], color='#bbb', lw=1.2, ls='--', zorder=3)

# Repository Interface layer
ax.text(ax2+aw/2, ay2+2.05, '[ Repository Interface ]', ha='center', fontsize=8,
        color=C_GOLD, fontweight='bold', zorder=3)
repos = ['IWeaponRepository', 'IAttachmentRepository',
         'ICustomRepository  (WeaponQueryRepository)']
for i, r in enumerate(repos):
    small_box(ax, ax2+0.15, ay2+1.6-i*0.48, aw-0.3, 0.38, C_BGGOLD, '#c9a000', r, fs=7.5, tc='#5a3e00')

# ════════════════════════════════
# 4. DuckDB 구현체
# ════════════════════════════════
dx, dy = 11.0, 5.2
dw, dh = 3.0, 4.0
box(ax, dx, dy, dw, dh, 'white', C_RED, lw=2)
header(ax, dx, dy+dh-0.58, dw, 0.58, C_RED, 'DuckDB 구현체', '현재 사용 중')
small_box(ax, dx+0.15, dy+dh-1.2, dw-0.3, 0.38, C_BGRED, C_RED, 'DuckDB WeaponRepository', fs=8)
small_box(ax, dx+0.15, dy+dh-1.65, dw-0.3, 0.38, C_BGRED, C_RED, 'DuckDB AttachmentRepository', fs=8)
small_box(ax, dx+0.15, dy+dh-2.1,  dw-0.3, 0.38, C_BGRED, C_RED, 'DuckDB CustomRepository', fs=8)
ax.plot([dx+0.1, dx+dw-0.1], [dy+1.45, dy+1.45], color='#ddd', lw=1, zorder=3)
ax.text(dx+dw/2, dy+1.35, '[ DuckDB SQL 예시 ]', ha='center', fontsize=7.5, color=C_RED, zorder=3)
sql_duck = [
    "SELECT w.weapon_id,",
    "  w.weapon_name, w.image_data",
    "FROM WEAPON w",
    "LEFT JOIN WEAPON_RECOIL r",
    "  ON w.weapon_id = r.weapon_id",
    "WHERE w.weapon_id = ?",
]
for i, line in enumerate(sql_duck):
    ax.text(dx+0.25, dy+1.1-i*0.185, line, fontsize=7,
            color='#7a0000', fontfamily='monospace', zorder=3)

# ════════════════════════════════
# 5. MySQL 구현체 (교체 가능)
# ════════════════════════════════
mx2, my2 = 11.0, 0.5
mw, mh = 3.0, 4.0
box(ax, mx2, my2, mw, mh, 'white', C_GREEN, lw=2)
header(ax, mx2, my2+mh-0.58, mw, 0.58, C_GREEN, 'MySQL 구현체', '교체 가능 (독립성)')
small_box(ax, mx2+0.15, my2+mh-1.2,  mw-0.3, 0.38, C_BGGREEN, C_GREEN, 'MySQL WeaponRepository', fs=8, tc='#1b4332')
small_box(ax, mx2+0.15, my2+mh-1.65, mw-0.3, 0.38, C_BGGREEN, C_GREEN, 'MySQL AttachmentRepository', fs=8, tc='#1b4332')
small_box(ax, mx2+0.15, my2+mh-2.1,  mw-0.3, 0.38, C_BGGREEN, C_GREEN, 'MySQL CustomRepository', fs=8, tc='#1b4332')
ax.plot([mx2+0.1, mx2+mw-0.1], [my2+1.45, my2+1.45], color='#ddd', lw=1, zorder=3)
ax.text(mx2+mw/2, my2+1.35, '[ MySQL SQL 예시 ]', ha='center', fontsize=7.5, color=C_GREEN, zorder=3)
sql_mysql = [
    "SELECT w.weapon_id,",
    "  w.weapon_name, w.image_data",
    "FROM WEAPON w",
    "LEFT JOIN WEAPON_RECOIL r",
    "  ON w.weapon_id = r.weapon_id",
    "WHERE w.weapon_id = %s;",
]
for i, line in enumerate(sql_mysql):
    ax.text(mx2+0.25, my2+1.1-i*0.185, line, fontsize=7,
            color='#1b4332', fontfamily='monospace', zorder=3)

# ════════════════════════════════
# 실제 DB
# ════════════════════════════════
# DuckDB 파일
box(ax, 15.2, 5.8, 2.4, 2.8, 'white', C_RED, lw=1.5, radius=0.15)
ax.text(16.4, 8.35, 'DuckDB', ha='center', fontsize=10, fontweight='bold', color=C_RED, zorder=3)
ax.text(16.4, 8.05, '.duckdb 파일', ha='center', fontsize=8, color='#555', zorder=3)
tables_d = ['WEAPON', 'ATTACHMENT', 'CUSTOM_CONFIG', 'RECOIL_RESULT']
for i, t in enumerate(tables_d):
    small_box(ax, 15.35, 8.0-0.48-i*0.45, 2.1, 0.36, C_BGRED, C_RED, t, fs=7.5)
ax.text(16.4, 6.0, 'image_data (base64)', ha='center', fontsize=7, color=C_GOLD, zorder=3)

# MySQL DB
box(ax, 15.2, 0.8, 2.4, 2.8, 'white', C_GREEN, lw=1.5, radius=0.15)
ax.text(16.4, 3.35, 'MySQL DB', ha='center', fontsize=10, fontweight='bold', color=C_GREEN, zorder=3)
ax.text(16.4, 3.05, 'RDB 서버', ha='center', fontsize=8, color='#555', zorder=3)
tables_m = ['WEAPON', 'ATTACHMENT', 'CUSTOM_CONFIG', 'RECOIL_RESULT']
for i, t in enumerate(tables_m):
    small_box(ax, 15.35, 3.0-0.48-i*0.45, 2.1, 0.36, C_BGGREEN, C_GREEN, t, fs=7.5, tc='#1b4332')
ax.text(16.4, 1.0, 'image_data (base64)', ha='center', fontsize=7, color=C_GOLD, zorder=3)

# ════════════════════════════════
# 화살표
# ════════════════════════════════
# 사용자 ↔ Flet GUI
arrow(ax, ux+1.05, uy+1.4, gx, uy+1.5, C_BLUE)
arrow(ax, gx, uy+1.2, ux+1.05, uy+1.1, C_BLUE, dash=True)
alabel(ax, (ux+1.05+gx)/2, uy+1.75, 'GUI 조작', C_BLUE, fs=8)
alabel(ax, (ux+1.05+gx)/2, uy+0.85, '화면 렌더링', C_BLUE, fs=8)

# Flet GUI ↔ App
arrow(ax, gx+gw, 5.5, ax2, 5.6, C_MAIN)
arrow(ax, ax2,   5.3, gx+gw, 5.2, C_MAIN, dash=True)
alabel(ax, (gx+gw+ax2)/2, 5.8,  '데이터 요청', C_MAIN, fs=8)
alabel(ax, (gx+gw+ax2)/2, 4.95, '결과 반환',   C_MAIN, fs=8)

# App ↔ DuckDB 구현체
arrow(ax, ax2+aw, 6.5, dx, 6.6, C_RED)
arrow(ax, dx, 6.3, ax2+aw, 6.2, C_RED, dash=True)
alabel(ax, (ax2+aw+dx)/2, 6.82, '인터페이스 호출', C_RED, fs=8)
alabel(ax, (ax2+aw+dx)/2, 5.98, 'DuckDB 구현',     C_RED, fs=8)

# App ↔ MySQL 구현체 (점선 — 교체 가능)
arrow(ax, ax2+aw, 3.8, mx2, 3.5, C_GREEN, dash=True)
arrow(ax, mx2, 3.2, ax2+aw, 3.0, C_GREEN, dash=True)
alabel(ax, (ax2+aw+mx2)/2+0.2, 3.75, '교체 가능', C_GREEN, fs=8)

# DuckDB 구현체 ↔ DuckDB DB
arrow(ax, dx+dw, 7.2, 15.2, 7.2, C_RED)
arrow(ax, 15.2,  6.9, dx+dw, 6.9, C_RED, dash=True)
alabel(ax, (dx+dw+15.2)/2, 7.45, 'SQL 쿼리', C_RED, fs=8)

# MySQL 구현체 ↔ MySQL DB
arrow(ax, mx2+mw, 2.5, 15.2, 2.5, C_GREEN)
arrow(ax, 15.2, 2.2, mx2+mw, 2.2, C_GREEN, dash=True)
alabel(ax, (mx2+mw+15.2)/2, 2.75, 'SQL 쿼리', C_GREEN, fs=8)

# 커스텀 저장 흐름
ax.annotate('', xy=(ax2+aw/2, ay2+0.2), xytext=(ux+0.5, uy-0.15),
    arrowprops=dict(arrowstyle='->', color=C_TEAL, lw=1.5,
                    linestyle=(0,(6,3)), connectionstyle='arc3,rad=-0.2'))
ax.text(4.3, 1.8, '파츠 선택 → 커스텀 저장', ha='center', fontsize=8.5, color=C_TEAL, zorder=4)

# Repository Pattern 설명 박스
box(ax, 0.3, 0.2, 4.5, 1.2, '#f0faf8', C_TEAL, lw=1.2, radius=0.15)
ax.text(2.55, 1.15, '[ Repository Pattern 독립성 ]', ha='center', fontsize=9,
        fontweight='bold', color='#1a6b63', zorder=3)
ax.text(2.55, 0.8,  '서비스 레이어는 Interface만 참조', ha='center', fontsize=8.5, color='#1a6b63', zorder=3)
ax.text(2.55, 0.5,  'DuckDB ↔ MySQL 구현체 교체 시 서비스 코드 변경 없음', ha='center', fontsize=8, color='#1a6b63', zorder=3)

# ── 범례 ──
lx, ly = 6.0, 1.1
ax.text(lx, ly+0.3, '범례', fontsize=9, fontweight='bold', color=C_TEXT)
items = [
    ('-',  C_MAIN,  '데이터 요청/응답'),
    ('--', C_MAIN,  '결과 반환'),
    ('--', C_GREEN, 'MySQL 교체 가능 (점선)'),
    ('--', C_TEAL,  '커스텀 저장 흐름'),
]
for i, (ls, c, label) in enumerate(items):
    lx2 = lx + (i % 2) * 3.5
    ly2 = ly - (i // 2) * 0.4
    dash = ls == '--'
    lnstyle = (0,(5,3)) if dash else '-'
    ax.plot([lx2, lx2+0.55], [ly2-0.15, ly2-0.15], color=c, lw=1.8, linestyle=lnstyle)
    ax.text(lx2+0.65, ly2-0.15, label, va='center', fontsize=8, color='#333')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GUNSMITH_구성도.png')
plt.tight_layout(pad=0.3)
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#f8f9fa')
plt.close()
print('저장 완료:', out)
