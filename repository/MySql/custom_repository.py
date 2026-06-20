import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
from datetime import datetime
import mysql.connector
from repository.i_custom_config_repository import ICustomConfigRepository
from repository.i_recoil_result_repository import IRecoilResultRepository
from repository.i_weapon_query_repository import IWeaponQueryRepository


class CustomConfigRepository(ICustomConfigRepository):

    def __init__(self, conn: mysql.connector.MySQLConnection):
        self.conn = conn

    def _df(self, sql: str, params=None) -> pd.DataFrame:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows)

    def _run(self, sql: str, params=None):
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        self.conn.commit()
        cursor.close()

    def _scalar(self, sql: str, params=None):
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None

    def save(self, df: pd.DataFrame):
        sql = """
            INSERT INTO CUSTOM_CONFIG
                (config_id, weapon_id, custom_name, muzzle_id, stock_id,
                 grip_id, magazine_id, scope_id, foregrip_id, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                custom_name=%s, muzzle_id=%s, stock_id=%s, grip_id=%s,
                magazine_id=%s, scope_id=%s, foregrip_id=%s
        """
        for _, r in df.iterrows():
            v = (r['config_id'], r['weapon_id'], r['custom_name'],
                 r['muzzle_id'], r['stock_id'], r['grip_id'],
                 r['magazine_id'], r['scope_id'], r['foregrip_id'], r['created_at'],
                 r['custom_name'], r['muzzle_id'], r['stock_id'], r['grip_id'],
                 r['magazine_id'], r['scope_id'], r['foregrip_id'])
            self._run(sql, v)

    def save_config(self, weapon_id: int, custom_name: str, slots: dict) -> int:
        new_id = (self._scalar("SELECT COALESCE(MAX(config_id), 0) FROM CUSTOM_CONFIG") or 0) + 1
        self._run(
            """INSERT INTO CUSTOM_CONFIG
               (config_id, weapon_id, custom_name, muzzle_id, stock_id, grip_id,
                magazine_id, scope_id, foregrip_id, created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (new_id, weapon_id, custom_name,
             slots.get('muzzle'), slots.get('stock'), slots.get('grip'),
             slots.get('magazine'), slots.get('scope'), slots.get('foregrip'),
             datetime.now())
        )
        return new_id

    def find_all(self) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM CUSTOM_CONFIG ORDER BY created_at DESC"
        )

    def find_all_with_weapon_name(self) -> pd.DataFrame:
        return self._df("""
            SELECT cc.config_id, cc.custom_name, w.weapon_name, w.gun_type,
                   cc.created_at
            FROM CUSTOM_CONFIG cc
            JOIN WEAPON w ON cc.weapon_id = w.weapon_id
            ORDER BY cc.created_at DESC
        """)

    def find_by_id(self, config_id: int) -> dict:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM CUSTOM_CONFIG WHERE config_id = %s", (config_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row if row else {}

    def find_all_by_weapon_id(self, weapon_id: int) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM CUSTOM_CONFIG WHERE weapon_id = %s ORDER BY created_at DESC",
            (weapon_id,)
        )

    def update(self, df: pd.DataFrame):
        sql = """
            UPDATE CUSTOM_CONFIG
            SET custom_name=%s, muzzle_id=%s, stock_id=%s, grip_id=%s,
                magazine_id=%s, scope_id=%s, foregrip_id=%s
            WHERE config_id = %s
        """
        for _, r in df.iterrows():
            self._run(sql, (
                r['custom_name'], r['muzzle_id'], r['stock_id'], r['grip_id'],
                r['magazine_id'], r['scope_id'], r['foregrip_id'], r['config_id']
            ))

    def delete_by_id(self, config_id: int) -> bool:
        self._run(
            "DELETE FROM CUSTOM_CONFIG WHERE config_id = %s", (config_id,)
        )
        return True


class RecoilResultRepository(IRecoilResultRepository):

    def __init__(self, conn: mysql.connector.MySQLConnection):
        self.conn = conn

    def _df(self, sql: str, params=None) -> pd.DataFrame:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows)

    def _run(self, sql: str, params=None):
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        self.conn.commit()
        cursor.close()

    def _scalar(self, sql: str, params=None):
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None

    def save(self, df: pd.DataFrame):
        sql = """
            INSERT INTO RECOIL_RESULT
                (result_id, config_id, final_recoil_vertical, final_recoil_horizontal,
                 final_muzzle_rise, final_muzzle_shake, final_first_shot_recoil,
                 final_recoil_recovery, stability_score, stability_grade)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                final_recoil_vertical=%s, final_recoil_horizontal=%s,
                final_muzzle_rise=%s, final_muzzle_shake=%s,
                final_first_shot_recoil=%s, final_recoil_recovery=%s,
                stability_score=%s, stability_grade=%s
        """
        for _, r in df.iterrows():
            v = (r['result_id'], r['config_id'],
                 r['final_recoil_vertical'], r['final_recoil_horizontal'],
                 r['final_muzzle_rise'], r['final_muzzle_shake'],
                 r['final_first_shot_recoil'], r['final_recoil_recovery'],
                 r['stability_score'], r['stability_grade'],
                 r['final_recoil_vertical'], r['final_recoil_horizontal'],
                 r['final_muzzle_rise'], r['final_muzzle_shake'],
                 r['final_first_shot_recoil'], r['final_recoil_recovery'],
                 r['stability_score'], r['stability_grade'])
            self._run(sql, v)

    def save_result(self, config_id: int, result: dict):
        new_id = (self._scalar("SELECT COALESCE(MAX(result_id), 0) FROM RECOIL_RESULT") or 0) + 1
        self._run(
            """INSERT INTO RECOIL_RESULT
               (result_id, config_id, final_recoil_vertical, final_recoil_horizontal,
                final_muzzle_rise, final_muzzle_shake, final_first_shot_recoil,
                final_recoil_recovery, stability_score, stability_grade)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (new_id, config_id,
             result['final_recoil_vertical'], result['final_recoil_horizontal'],
             result['final_muzzle_rise'], result['final_muzzle_shake'],
             result['final_first_shot_recoil'], result['final_recoil_recovery'],
             result['stability_score'], result['stability_grade'])
        )

    def find_by_config_id(self, config_id: int) -> dict:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM RECOIL_RESULT WHERE config_id = %s", (config_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row if row else {}

    def update(self, df: pd.DataFrame):
        sql = """
            UPDATE RECOIL_RESULT
            SET final_recoil_vertical=%s, final_recoil_horizontal=%s,
                final_muzzle_rise=%s, final_muzzle_shake=%s,
                final_first_shot_recoil=%s, final_recoil_recovery=%s,
                stability_score=%s, stability_grade=%s
            WHERE config_id = %s
        """
        for _, r in df.iterrows():
            self._run(sql, (
                r['final_recoil_vertical'], r['final_recoil_horizontal'],
                r['final_muzzle_rise'], r['final_muzzle_shake'],
                r['final_first_shot_recoil'], r['final_recoil_recovery'],
                r['stability_score'], r['stability_grade'],
                r['config_id']
            ))

    def delete_by_config_id(self, config_id: int) -> bool:
        self._run(
            "DELETE FROM RECOIL_RESULT WHERE config_id = %s", (config_id,)
        )
        return True


class WeaponQueryRepository(IWeaponQueryRepository):
    """복합 JOIN 쿼리 전용 레포지토리"""

    def __init__(self, conn: mysql.connector.MySQLConnection):
        self.conn = conn

    def _df(self, sql: str, params=None) -> pd.DataFrame:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(rows)

    def find_all_weapons_with_grade(self) -> pd.DataFrame:
        """WEAPON LEFT JOIN WEAPON_RECOIL — 전체 총기 + 안정성 등급"""
        return self._df("""
            SELECT w.weapon_id, w.weapon_name, w.gun_type, w.bullet_type,
                   w.damage, w.fire_speed, w.is_custom, w.image_data,
                   r.stability_score, r.stability_grade
            FROM WEAPON w
            LEFT JOIN WEAPON_RECOIL r ON w.weapon_id = r.weapon_id
            ORDER BY w.gun_type, w.weapon_name
        """)

    def find_weapons_by_type(self, gun_type: str) -> pd.DataFrame:
        return self._df("""
            SELECT w.weapon_id, w.weapon_name, w.gun_type, w.bullet_type,
                   w.damage, w.fire_speed, w.is_custom, w.image_data,
                   r.stability_score, r.stability_grade
            FROM WEAPON w
            LEFT JOIN WEAPON_RECOIL r ON w.weapon_id = r.weapon_id
            WHERE w.gun_type = %s
            ORDER BY w.weapon_name
        """, (gun_type,))

    def find_weapon_with_recoil(self, weapon_id: int) -> dict:
        """WEAPON JOIN WEAPON_RECOIL — 총기 상세 + 반동 스탯"""
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT w.weapon_id, w.weapon_name, w.gun_type, w.bullet_type,
                   w.damage, w.bullet_speed, w.fire_speed, w.description,
                   w.is_custom, w.image_data,
                   r.recoil_vertical, r.recoil_horizontal, r.pattern_scale,
                   r.first_recoil, r.crouch_modifier, r.prone_modifier,
                   r.muzzle_rise, r.muzzle_shake, r.recovery_recoil,
                   r.vertical_speed, r.stability_score, r.stability_grade
            FROM WEAPON w
            LEFT JOIN WEAPON_RECOIL r ON w.weapon_id = r.weapon_id
            WHERE w.weapon_id = %s
        """, (weapon_id,))
        row = cursor.fetchone()
        cursor.close()
        if not row:
            return {}
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
        return self._df("""
            SELECT w.weapon_name,
                   a.attachment_id, a.attachment_name, a.slot_type, a.image_data,
                   c.control_recoil_vertical, c.control_recoil_horizontal,
                   c.control_muzzle_rise,     c.control_muzzle_shake,
                   c.mod_recovery_recoil,     c.control_first_recoil
            FROM WEAPON w
            JOIN WEAPON_ATTACHMENT_COMPAT c ON w.weapon_id = c.weapon_id
            JOIN ATTACHMENT a               ON c.attachment_id = a.attachment_id
            WHERE w.weapon_id = %s
            ORDER BY a.slot_type, a.attachment_name
        """, (weapon_id,))

    def find_compare_results(self, config_id_left: int, config_id_right: int) -> pd.DataFrame:
        """CUSTOM_CONFIG LEFT JOIN RECOIL_RESULT — 커스텀 비교"""
        return self._df("""
            SELECT cc.config_id, cc.custom_name, w.weapon_name, w.gun_type,
                   rr.final_recoil_vertical,   rr.final_recoil_horizontal,
                   rr.final_muzzle_rise,        rr.final_muzzle_shake,
                   rr.final_first_shot_recoil,  rr.final_recoil_recovery,
                   rr.stability_score,          rr.stability_grade
            FROM CUSTOM_CONFIG cc
            LEFT JOIN RECOIL_RESULT rr ON cc.config_id = rr.config_id
            LEFT JOIN WEAPON w         ON cc.weapon_id  = w.weapon_id
            WHERE cc.config_id IN (%s, %s)
            ORDER BY cc.config_id
        """, (config_id_left, config_id_right))
