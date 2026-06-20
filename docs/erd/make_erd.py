import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(24, 15))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.set_xlim(0, 24)
ax.set_ylim(0, 15)
ax.axis('off')

HDR  = '#1e2535'
BODY = '#161b27'
ACC  = '#4fc3f7'
TXT  = '#dde3ed'
DIM  = '#6b7585'
GRN  = '#66BB6A'
BDR  = '#252d3f'

def draw_table(ax, x, y, w, h, title, cols):
    ax.add_patch(FancyBboxPatch((x, y+h-0.6), w, 0.6,
        boxstyle='round,pad=0.02', facecolor=HDR, edgecolor=ACC, linewidth=2.0, zorder=3))
    ax.text(x+w/2, y+h-0.3, title, color=ACC, fontsize=8.5,
            fontweight='bold', ha='center', va='center',
            fontfamily='monospace', zorder=4)
    body_h = h - 0.6
    ax.add_patch(FancyBboxPatch((x, y), w, body_h,
        boxstyle='round,pad=0.02', facecolor=BODY, edgecolor=BDR, linewidth=1.0, zorder=2))
    row_h = body_h / max(len(cols), 1)
    for i, (pk, name, dtype) in enumerate(cols):
        ry = y + body_h - (i+1)*row_h
        if i > 0:
            ax.plot([x+0.05, x+w-0.05], [ry+row_h, ry+row_h],
                    color=BDR, linewidth=0.5, zorder=3)
        if pk == 'PK':
            ax.text(x+0.13, ry+row_h/2, 'PK', color='#FFD700', fontsize=5.5,
                    fontweight='bold', va='center', zorder=4)
        elif pk == 'FK':
            ax.text(x+0.13, ry+row_h/2, 'FK', color='#ff9800', fontsize=5.5,
                    fontweight='bold', va='center', zorder=4)
        ax.text(x+0.38, ry+row_h/2, name, color=TXT, fontsize=6,
                va='center', fontfamily='monospace', zorder=4)
        ax.text(x+w-0.1, ry+row_h/2, dtype, color=DIM, fontsize=5.2,
                va='center', ha='right', fontfamily='monospace', zorder=4)

# WEAPON (중앙 상단)
WX, WY, WW, WH = 8.5, 9.0, 5.2, 5.2
draw_table(ax, WX, WY, WW, WH, 'WEAPON', [
    ('PK','weapon_id','INT'),
    ('',  'weapon_name','VARCHAR(50)'),
    ('',  'gun_type','VARCHAR(10)'),
    ('',  'bullet_type','VARCHAR(15)'),
    ('',  'damage','FLOAT'),
    ('',  'bullet_speed','FLOAT'),
    ('',  'fire_speed','FLOAT'),
    ('',  'description','TEXT'),
    ('',  'is_custom','BOOLEAN'),
    ('',  'image_data','TEXT'),
])

# WEAPON_RECOIL (우측 상단)
draw_table(ax, 15.0, 9.0, 5.2, 5.2, 'WEAPON_RECOIL', [
    ('PK','recoil_id','INT'),
    ('FK','weapon_id','INT'),
    ('',  'recoil_vertical','FLOAT'),
    ('',  'recoil_horizontal','FLOAT'),
    ('',  'first_recoil','FLOAT'),
    ('',  'muzzle_rise','FLOAT'),
    ('',  'muzzle_shake','FLOAT'),
    ('',  'recovery_recoil','FLOAT'),
    ('',  'stability_score','INT'),
    ('',  'stability_grade','VARCHAR(1)'),
])

# ATTACHMENT (좌측 상단)
draw_table(ax, 2.0, 9.0, 5.2, 5.2, 'ATTACHMENT', [
    ('PK','attachment_id','INT'),
    ('',  'attachment_name','VARCHAR(60)'),
    ('',  'slot_type','VARCHAR(15)'),
    ('',  'image_data','TEXT'),
    ('',  'control_recoil_vertical','FLOAT'),
    ('',  'control_recoil_horizontal','FLOAT'),
    ('',  'control_muzzle_rise','FLOAT'),
    ('',  'control_muzzle_shake','FLOAT'),
    ('',  'mod_recovery_recoil','FLOAT'),
    ('',  'control_first_recoil','FLOAT'),
])

# WEAPON_ATTACHMENT_COMPAT (중앙 하단)
draw_table(ax, 6.8, 2.5, 5.5, 5.0, 'WEAPON_ATTACHMENT_COMPAT', [
    ('PK','compat_id','INT'),
    ('FK','weapon_id','INT'),
    ('FK','attachment_id','INT'),
    ('',  'control_recoil_vertical','FLOAT'),
    ('',  'control_recoil_horizontal','FLOAT'),
    ('',  'control_muzzle_rise','FLOAT'),
    ('',  'control_muzzle_shake','FLOAT'),
    ('',  'mod_recovery_recoil','FLOAT'),
    ('',  'control_first_recoil','FLOAT'),
])

# CUSTOM_CONFIG (좌측 하단)
draw_table(ax, 0.5, 2.5, 5.2, 5.0, 'CUSTOM_CONFIG', [
    ('PK','config_id','INT'),
    ('FK','weapon_id','INT'),
    ('',  'custom_name','VARCHAR(50)'),
    ('FK','muzzle_id','INT'),
    ('FK','stock_id','INT'),
    ('FK','grip_id','INT'),
    ('FK','magazine_id','INT'),
    ('FK','scope_id','INT'),
    ('FK','foregrip_id','INT'),
    ('',  'created_at','TIMESTAMP'),
])

# RECOIL_RESULT (우측 하단)
draw_table(ax, 13.5, 2.5, 5.2, 5.0, 'RECOIL_RESULT', [
    ('PK','result_id','INT'),
    ('FK','config_id','INT'),
    ('',  'final_recoil_vertical','FLOAT'),
    ('',  'final_recoil_horizontal','FLOAT'),
    ('',  'final_muzzle_rise','FLOAT'),
    ('',  'final_muzzle_shake','FLOAT'),
    ('',  'final_first_shot_recoil','FLOAT'),
    ('',  'final_recoil_recovery','FLOAT'),
    ('',  'stability_score','INT'),
    ('',  'stability_grade','VARCHAR(1)'),
])

def crow_one(ax, x, y, direction):
    if direction == 'left':
        ax.plot([x, x], [y-0.13, y+0.13], color=ACC, lw=1.8, zorder=5)
        ax.plot([x+0.1, x+0.1], [y-0.13, y+0.13], color=ACC, lw=1.8, zorder=5)
    elif direction == 'right':
        ax.plot([x, x], [y-0.13, y+0.13], color=ACC, lw=1.8, zorder=5)
        ax.plot([x-0.1, x-0.1], [y-0.13, y+0.13], color=ACC, lw=1.8, zorder=5)
    elif direction == 'bottom':
        ax.plot([x-0.13, x+0.13], [y, y], color=ACC, lw=1.8, zorder=5)
        ax.plot([x-0.13, x+0.13], [y+0.1, y+0.1], color=ACC, lw=1.8, zorder=5)
    elif direction == 'top':
        ax.plot([x-0.13, x+0.13], [y, y], color=ACC, lw=1.8, zorder=5)
        ax.plot([x-0.13, x+0.13], [y-0.1, y-0.1], color=ACC, lw=1.8, zorder=5)

def crow_many(ax, x, y, direction):
    if direction == 'left':
        ax.plot([x, x+0.22], [y, y], color=GRN, lw=1.5, zorder=5)
        ax.plot([x, x+0.18], [y+0.13, y], color=GRN, lw=1.5, zorder=5)
        ax.plot([x, x+0.18], [y-0.13, y], color=GRN, lw=1.5, zorder=5)
    elif direction == 'right':
        ax.plot([x, x-0.22], [y, y], color=GRN, lw=1.5, zorder=5)
        ax.plot([x, x-0.18], [y+0.13, y], color=GRN, lw=1.5, zorder=5)
        ax.plot([x, x-0.18], [y-0.13, y], color=GRN, lw=1.5, zorder=5)
    elif direction == 'top':
        ax.plot([x, x], [y, y-0.22], color=GRN, lw=1.5, zorder=5)
        ax.plot([x-0.13, x], [y-0.18, y], color=GRN, lw=1.5, zorder=5)
        ax.plot([x+0.13, x], [y-0.18, y], color=GRN, lw=1.5, zorder=5)
    elif direction == 'bottom':
        ax.plot([x, x], [y, y+0.22], color=GRN, lw=1.5, zorder=5)
        ax.plot([x-0.13, x], [y+0.18, y], color=GRN, lw=1.5, zorder=5)
        ax.plot([x+0.13, x], [y+0.18, y], color=GRN, lw=1.5, zorder=5)

def rel(ax, pts, color=ACC):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, lw=1.3, linestyle='--', alpha=0.9, zorder=3)

# 1. WEAPON 1:1 WEAPON_RECOIL  (오른쪽으로)
rel(ax, [(WX+WW, 11.6), (15.0, 11.6)])
crow_one(ax, WX+WW, 11.6, 'right')
crow_one(ax, 15.0, 11.6, 'left')
ax.text(14.5, 11.85, '1:1', color=DIM, fontsize=7, ha='center', fontweight='bold')

# 2. WEAPON 1:N WEAPON_ATTACHMENT_COMPAT  (아래로)
rel(ax, [(11.1, WY), (11.1, 7.5)], color=GRN)
crow_one(ax, 11.1, WY, 'bottom')
crow_many(ax, 11.1, 7.5, 'top')
ax.text(11.55, 8.2, '1:N', color=DIM, fontsize=7, ha='center', fontweight='bold')

# 3. ATTACHMENT 1:N WEAPON_ATTACHMENT_COMPAT  (오른쪽+아래)
rel(ax, [(7.2, 10.5), (6.0, 10.5), (6.0, 6.6), (6.8, 6.6)], color=GRN)
crow_one(ax, 7.2, 10.5, 'left')
crow_many(ax, 6.8, 6.6, 'left')
ax.text(5.6, 8.5, '1:N', color=DIM, fontsize=7, ha='center', fontweight='bold')

# 4. WEAPON 1:N CUSTOM_CONFIG  (왼쪽+아래)
rel(ax, [(WX, 10.8), (3.0, 10.8), (3.0, 7.5)], color=GRN)
crow_one(ax, WX, 10.8, 'left')
crow_many(ax, 3.0, 7.5, 'top')
ax.text(5.5, 11.05, '1:N', color=DIM, fontsize=7, ha='center', fontweight='bold')

# 5. ATTACHMENT 1:N CUSTOM_CONFIG  (아래로, muzzle/stock/grip FK)
rel(ax, [(2.0, 9.0), (1.5, 9.0), (1.5, 7.5)], color=GRN)
crow_one(ax, 2.0, 9.0, 'left')
crow_many(ax, 1.5, 7.5, 'top')
ax.text(0.9, 8.2, '1:N', color=DIM, fontsize=6.5, ha='center', fontweight='bold')

# 6. CUSTOM_CONFIG 1:1 RECOIL_RESULT  (오른쪽으로)
rel(ax, [(5.7, 5.0), (13.5, 5.0)])
crow_one(ax, 5.7, 5.0, 'right')
crow_one(ax, 13.5, 5.0, 'left')
ax.text(9.6, 5.25, '1:1', color=DIM, fontsize=7, ha='center', fontweight='bold')

# 타이틀
ax.text(12.0, 14.6, "GUNSMITH  ERD  —  Crow's Foot Notation",
        color=ACC, fontsize=14, fontweight='bold', ha='center',
        fontfamily='monospace')
ax.text(12.0, 14.1,
        'DB: DuckDB  |  Tables: 6  |  Relations: 6  |  20231161 쳍승환',
        color=DIM, fontsize=7.5, ha='center')

# 범례
legend_items = [
    mpatches.Patch(color='#FFD700', label='Primary Key (PK)'),
    mpatches.Patch(color='#ff9800', label='Foreign Key (FK)'),
    mpatches.Patch(color=ACC, label='1:1 (|| — ||)'),
    mpatches.Patch(color=GRN, label='1:N (|| — <)'),
]
leg = ax.legend(handles=legend_items, loc='lower right',
          facecolor=HDR, edgecolor=BDR, labelcolor=TXT, fontsize=8,
          framealpha=0.9, title='Legend', title_fontsize=8)
leg.get_title().set_color(ACC)

plt.tight_layout(pad=0.3)
out = r'C:/Users/user/DB_2026/GUNSMITH/docs/erd/GUNSMITH_ERD.png'
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor='#0d1117')
print('saved:', out)
