import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
from datetime import datetime
from repository.i_custom_config_repository import ICustomConfigRepository
from repository.i_recoil_result_repository import IRecoilResultRepository
from repository.i_weapon_query_repository import IWeaponQueryRepository
from database import Database


class CustomConfigRepository(ICustomConfigRepository):

    def __init__(self, db: Database):
        self.db = db

    def save(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "INSERT OR REPLACE INTO CUSTOM_CONFIG VALUES (?,?,?,?,?,?,?,?,?,?)", list(r)
            )

    def save_config(self, weapon_id: int, custom_name: str, slots: dict) -> int:
        """새 커스텀 설정 저장, 부여된 config_id 반환"""
        new_id = (self.db.scalar("SELECT COALESCE(MAX(config_id),0) FROM CUSTOM_CONFIG") or 0) + 1
        self.db.run(
            """INSERT INTO CUSTOM_CONFIG
               (config_id, weapon_id, custom_name, muzzle_id, stock_id, grip_id,
                magazine_id, scope_id, foregrip_id, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [new_id, weapon_id, custom_name,
             slots.get('muzzle'), slots.get('stock'), slots.get('grip'),
             slots.get('magazine'), slots.get('scope'), slots.get('foregrip'),
             datetime.now()]
        )
        return new_id

    def find_all(self) -> pd.DataFrame:
        return self.db.q(
            "SELECT * FROM CUSTOM_CONFIG ORDER BY created_at DESC"
        )

    def find_all_with_weapon_name(self) -> pd.DataFrame:
        return self.db.q("""
            SELECT cc.config_id, cc.custom_name, w.weapon_name, w.gun_type,
                   cc.created_at
            FROM CUSTOM_CONFIG cc
            JOIN WEAPON w ON cc.weapon_id = w.weapon_id
            ORDER BY cc.created_at DESC
        """)

    def find_by_id(self, config_id: int) -> dict:
        df = self.db.q("SELECT * FROM CUSTOM_CONFIG WHERE config_id=?", [config_id])
        return df.iloc[0].to_dict() if not df.empty else {}

    def find_all_by_weapon_id(self, weapon_id: int) -> pd.DataFrame:
        return self.db.q(
            "SELECT * FROM CUSTOM_CONFIG WHERE weapon_id=? ORDER BY created_at DESC",
            [weapon_id]
        )

    def update(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                """UPDATE CUSTOM_CONFIG SET custom_name=?, muzzle_id=?, stock_id=?,
                   grip_id=?, magazine_id=?, scope_id=?, foregrip_id=?
                   WHERE config_id=?""",
                [r['custom_name'], r['muzzle_id'], r['stock_id'], r['grip_id'],
                 r['magazine_id'], r['scope_id'], r['foregrip_id'], r['config_id']]
            )

    def delete_by_id(self, config_id: int) -> bool:
        self.db.run("DELETE FROM CUSTOM_CONFIG WHERE config_id=?", [config_id])
        return True


class RecoilResultRepository(IRecoilResultRepository):

    def __init__(self, db: Database):
        self.db = db

    def save(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "INSERT OR REPLACE INTO RECOIL_RESULT VALUES (?,?,?,?,?,?,?,?,?,?)", list(r)
            )

    def save_result(self, config_id: int, result: dict):
        new_id = (self.db.scalar("SELECT COALESCE(MAX(result_id),0) FROM RECOIL_RESULT") or 0) + 1
        self.db.run(
            """INSERT INTO RECOIL_RESULT
               (result_id, config_id, final_recoil_vertical, final_recoil_horizontal,
                final_muzzle_rise, final_muzzle_shake, final_first_shot_recoil,
                final_recoil_recovery, stability_score, stability_grade)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [new_id, config_id,
             result['final_recoil_vertical'], result['final_recoil_horizontal'],
             result['final_muzzle_rise'], result['final_muzzle_shake'],
             result['final_first_shot_recoil'], result['final_recoil_recovery'],
             result['stability_score'], result['stability_grade']]
        )

    def find_by_config_id(self, config_id: int) -> dict:
        df = self.db.q("SELECT * FROM RECOIL_RESULT WHERE config_id=?", [config_id])
        return df.iloc[0].to_dict() if not df.empty else {}

    def update(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                """UPDATE RECOIL_RESULT SET final_recoil_vertical=?, final_recoil_horizontal=?,
                   final_muzzle_rise=?, final_muzzle_shake=?, final_first_shot_recoil=?,
                   final_recoil_recovery=?, stability_score=?, stability_grade=?
                   WHERE config_id=?""",
                [r['final_recoil_vertical'], r['final_recoil_horizontal'],
                 r['final_muzzle_rise'], r['final_muzzle_shake'],
                 r['final_first_shot_recoil'], r['final_recoil_recovery'],
                 r['stability_score'], r['stability_grade'], r['config_id']]
            )

    def delete_by_config_id(self, config_id: int) -> bool:
        self.db.run("DELETE FROM RECOIL_RESULT WHERE config_id=?", [config_id])
        return True


class WeaponQueryRepository(IWeaponQueryRepository):
    """복합 JOIN 쿼리 전용 레포지토리"""

    def __init__(self, db: Database):
        self.db = db

    def find_all_weapons_with_grade(self) -> pd.DataFrame:
        """WEAPON LEFT JOIN WEAPON_RECOIL — 전체 총기 + 안정성 등급"""
        return self.db.q("""
            SELECT w.weapon_id, w.weapon_name, w.gun_type, w.bullet_type,
                   w.damage, w.fire_speed, w.is_custom, w.image_data,
                   r.stability_score, r.stability_grade
            FROM WEAPON w
            LEFT JOIN WEAPON_RECOIL r ON w.weapon_id = r.weapon_id
            ORDER BY w.gun_type, w.weapon_name
        """)

    def find_weapons_by_type(self, gun_type: str) -> pd.DataFrame:
        return self.db.q("""
            SELECT w.weapon_id, w.weapon_name, w.gun_type, w.bullet_type,
                   w.damage, w.fire_speed, w.is_custom, w.image_data,
                   r.stability_score, r.stability_grade
            FROM WEAPON w
            LEFT JOIN WEAPON_RECOIL r ON w.weapon_id = r.weapon_id
            WHERE w.gun_type = ?
            ORDER BY w.weapon_name
        """, [gun_type])

    def find_weapon_with_recoil(self, weapon_id: int) -> dict:
        """WEAPON JOIN WEAPON_RECOIL — 총기 상세 + 반동 스탯"""
        df = self.db.q("""
            SELECT w.weapon_id, w.weapon_name, w.gun_type, w.bullet_type,
                   w.damage, w.bullet_speed, w.fire_speed, w.description,
                   w.is_custom, w.image_data,
                   r.recoil_vertical, r.recoil_horizontal, r.pattern_scale,
                   r.first_recoil, r.crouch_modifier, r.prone_modifier,
                   r.muzzle_rise, r.muzzle_shake, r.recovery_recoil,
                   r.vertical_speed, r.stability_score, r.stability_grade
            FROM WEAPON w
            LEFT JOIN WEAPON_RECOIL r ON w.weapon_id = r.weapon_id
            WHERE w.weapon_id = ?
        """, [weapon_id])
        if df.empty:
            return {}
        row = df.iloc[0].to_dict()
        weapon_cols = ['weapon_id','weapon_name','gun_type','bullet_type','damage',
                       'bullet_speed','fire_speed','description','is_custom','image_data']
        recoil_cols = ['recoil_vertical','recoil_horizontal','pattern_scale','first_recoil',
                       'crouch_modifier','prone_modifier','muzzle_rise','muzzle_shake',
                       'recovery_recoil','vertical_speed','stability_score','stability_grade']
        return {
            'weapon': {k: row.get(k) for k in weapon_cols},
            'recoil': {k: row.get(k) for k in recoil_cols},
        }

    def find_compat_parts_by_weapon(self, weapon_id: int) -> pd.DataFrame:
        """3-way JOIN: WEAPON + WEAPON_ATTACHMENT_COMPAT + ATTACHMENT"""
        return self.db.q("""
            SELECT w.weapon_name,
                   a.attachment_id, a.attachment_name, a.slot_type, a.image_data,
                   c.control_recoil_vertical, c.control_recoil_horizontal,
                   c.control_muzzle_rise,     c.control_muzzle_shake,
                   c.mod_recovery_recoil,     c.control_first_recoil
            FROM WEAPON w
            JOIN WEAPON_ATTACHMENT_COMPAT c ON w.weapon_id = c.weapon_id
            JOIN ATTACHMENT a               ON c.attachment_id = a.attachment_id
            WHERE w.weapon_id = ?
            ORDER BY a.slot_type, a.attachment_name
        """, [weapon_id])

    def find_compare_results(self, config_id_left: int, config_id_right: int) -> pd.DataFrame:
        """CUSTOM_CONFIG LEFT JOIN RECOIL_RESULT — 커스텀 비교"""
        return self.db.q("""
            SELECT cc.config_id, cc.custom_name, w.weapon_name, w.gun_type,
                   rr.final_recoil_vertical,   rr.final_recoil_horizontal,
                   rr.final_muzzle_rise,        rr.final_muzzle_shake,
                   rr.final_first_shot_recoil,  rr.final_recoil_recovery,
                   rr.stability_score,          rr.stability_grade
            FROM CUSTOM_CONFIG cc
            LEFT JOIN RECOIL_RESULT rr ON cc.config_id = rr.config_id
            LEFT JOIN WEAPON w         ON cc.weapon_id  = w.weapon_id
            WHERE cc.config_id IN (?, ?)
            ORDER BY cc.config_id
        """, [config_id_left, config_id_right])
