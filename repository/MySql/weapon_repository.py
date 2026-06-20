import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import mysql.connector
from repository.i_weapon_repository import IWeaponRepository
from repository.i_weapon_recoil_repository import IWeaponRecoilRepository


class WeaponRepository(IWeaponRepository):

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

    def save(self, df: pd.DataFrame):
        sql = """
            INSERT INTO WEAPON
                (weapon_id, weapon_name, gun_type, bullet_type, damage,
                 bullet_speed, fire_speed, description, is_custom, image_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                weapon_name=%s, gun_type=%s, bullet_type=%s, damage=%s,
                bullet_speed=%s, fire_speed=%s, description=%s,
                is_custom=%s, image_data=%s
        """
        for _, r in df.iterrows():
            v = (r['weapon_id'], r['weapon_name'], r['gun_type'], r['bullet_type'],
                 r['damage'], r['bullet_speed'], r['fire_speed'], r['description'],
                 r['is_custom'], r['image_data'],
                 r['weapon_name'], r['gun_type'], r['bullet_type'], r['damage'],
                 r['bullet_speed'], r['fire_speed'], r['description'],
                 r['is_custom'], r['image_data'])
            self._run(sql, v)

    def find_all(self) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM WEAPON ORDER BY gun_type, weapon_name"
        )

    def find_by_id(self, weapon_id: int) -> dict:
        df = self._df(
            "SELECT * FROM WEAPON WHERE weapon_id = %s", (weapon_id,)
        )
        return df.iloc[0].to_dict() if not df.empty else {}

    def find_all_by_type(self, gun_type: str) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM WEAPON WHERE gun_type = %s ORDER BY weapon_name",
            (gun_type,)
        )

    def find_by_keyword(self, keyword: str) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM WEAPON WHERE weapon_name LIKE %s ORDER BY weapon_name",
            (f"%{keyword}%",)
        )

    def update(self, df: pd.DataFrame):
        sql = """
            UPDATE WEAPON
            SET weapon_name=%s, gun_type=%s, bullet_type=%s, damage=%s,
                bullet_speed=%s, fire_speed=%s, description=%s,
                is_custom=%s, image_data=%s
            WHERE weapon_id = %s
        """
        for _, r in df.iterrows():
            self._run(sql, (
                r['weapon_name'], r['gun_type'], r['bullet_type'], r['damage'],
                r['bullet_speed'], r['fire_speed'], r['description'],
                r['is_custom'], r['image_data'], r['weapon_id']
            ))

    def delete_by_id(self, weapon_id: int) -> bool:
        self._run("DELETE FROM WEAPON WHERE weapon_id = %s", (weapon_id,))
        return True


class WeaponRecoilRepository(IWeaponRecoilRepository):

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

    def save(self, df: pd.DataFrame):
        sql = """
            INSERT INTO WEAPON_RECOIL
                (recoil_id, weapon_id, recoil_vertical, recoil_horizontal,
                 pattern_scale, first_recoil, crouch_modifier, prone_modifier,
                 muzzle_rise, muzzle_shake, recovery_recoil, vertical_speed,
                 stability_score, stability_grade)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                recoil_vertical=%s, recoil_horizontal=%s, pattern_scale=%s,
                first_recoil=%s, crouch_modifier=%s, prone_modifier=%s,
                muzzle_rise=%s, muzzle_shake=%s, recovery_recoil=%s,
                vertical_speed=%s, stability_score=%s, stability_grade=%s
        """
        for _, r in df.iterrows():
            v = (r['recoil_id'], r['weapon_id'], r['recoil_vertical'], r['recoil_horizontal'],
                 r['pattern_scale'], r['first_recoil'], r['crouch_modifier'], r['prone_modifier'],
                 r['muzzle_rise'], r['muzzle_shake'], r['recovery_recoil'], r['vertical_speed'],
                 r['stability_score'], r['stability_grade'],
                 r['recoil_vertical'], r['recoil_horizontal'], r['pattern_scale'],
                 r['first_recoil'], r['crouch_modifier'], r['prone_modifier'],
                 r['muzzle_rise'], r['muzzle_shake'], r['recovery_recoil'],
                 r['vertical_speed'], r['stability_score'], r['stability_grade'])
            self._run(sql, v)

    def find_by_weapon_id(self, weapon_id: int) -> dict:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM WEAPON_RECOIL WHERE weapon_id = %s", (weapon_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row if row else {}

    def update(self, df: pd.DataFrame):
        sql = """
            UPDATE WEAPON_RECOIL
            SET recoil_vertical=%s, recoil_horizontal=%s, pattern_scale=%s,
                first_recoil=%s, crouch_modifier=%s, prone_modifier=%s,
                muzzle_rise=%s, muzzle_shake=%s, recovery_recoil=%s,
                vertical_speed=%s, stability_score=%s, stability_grade=%s
            WHERE weapon_id = %s
        """
        for _, r in df.iterrows():
            self._run(sql, (
                r['recoil_vertical'], r['recoil_horizontal'], r['pattern_scale'],
                r['first_recoil'], r['crouch_modifier'], r['prone_modifier'],
                r['muzzle_rise'], r['muzzle_shake'], r['recovery_recoil'],
                r['vertical_speed'], r['stability_score'], r['stability_grade'],
                r['weapon_id']
            ))

    def delete_by_weapon_id(self, weapon_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM WEAPON_RECOIL WHERE weapon_id = %s", (weapon_id,)
        )
        self.conn.commit()
        cursor.close()
        return True
