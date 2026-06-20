"""
3-Table JOIN Demo
WEAPON JOIN WEAPON_ATTACHMENT_COMPAT JOIN ATTACHMENT
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Database

db = Database()

print("=" * 70)
print("  3-Table JOIN: WEAPON ⋈ WEAPON_ATTACHMENT_COMPAT ⋈ ATTACHMENT")
print("=" * 70)
print()

df = db.q("""
    SELECT
        w.weapon_name   AS 총기명,
        a.slot_type     AS 슬롯,
        a.attachment_name AS 파츠명,
        c.control_recoil_vertical   AS 수직반동보정,
        c.control_recoil_horizontal AS 좌우반동보정,
        c.control_muzzle_rise       AS 총구들림보정
    FROM WEAPON w
    JOIN WEAPON_ATTACHMENT_COMPAT c ON w.weapon_id = c.weapon_id
    JOIN ATTACHMENT a               ON c.attachment_id = a.attachment_id
    WHERE w.weapon_name = 'M416'
    ORDER BY a.slot_type, a.attachment_name
""")

print(df.to_string(index=False))
print()
print(f"  총 {len(df)}개 행 반환")
print()
print("SQL:")
print("""
    SELECT w.weapon_name, a.slot_type, a.attachment_name,
           c.control_recoil_vertical, c.control_recoil_horizontal,
           c.control_muzzle_rise
    FROM WEAPON w
    JOIN WEAPON_ATTACHMENT_COMPAT c ON w.weapon_id = c.weapon_id
    JOIN ATTACHMENT a               ON c.attachment_id = a.attachment_id
    WHERE w.weapon_name = 'M416'
    ORDER BY a.slot_type, a.attachment_name
""")
