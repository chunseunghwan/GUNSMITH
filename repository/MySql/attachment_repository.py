import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
import mysql.connector
from repository.i_attachment_repository import IAttachmentRepository
from repository.I_weapon_attachment_compat_repository import IWeaponAttachmentCompatRepository


class AttachmentRepository(IAttachmentRepository):

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
            INSERT INTO ATTACHMENT
                (attachment_id, attachment_name, slot_type, image_data,
                 control_recoil_vertical, control_recoil_horizontal,
                 control_muzzle_rise, control_muzzle_shake,
                 mod_recovery_recoil, control_first_recoil)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                attachment_name=%s, slot_type=%s, image_data=%s,
                control_recoil_vertical=%s, control_recoil_horizontal=%s,
                control_muzzle_rise=%s, control_muzzle_shake=%s,
                mod_recovery_recoil=%s, control_first_recoil=%s
        """
        for _, r in df.iterrows():
            v = (r['attachment_id'], r['attachment_name'], r['slot_type'], r['image_data'],
                 r['control_recoil_vertical'], r['control_recoil_horizontal'],
                 r['control_muzzle_rise'], r['control_muzzle_shake'],
                 r['mod_recovery_recoil'], r['control_first_recoil'],
                 r['attachment_name'], r['slot_type'], r['image_data'],
                 r['control_recoil_vertical'], r['control_recoil_horizontal'],
                 r['control_muzzle_rise'], r['control_muzzle_shake'],
                 r['mod_recovery_recoil'], r['control_first_recoil'])
            self._run(sql, v)

    def find_all(self) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM ATTACHMENT ORDER BY slot_type, attachment_name"
        )

    def find_by_id(self, attachment_id: int) -> dict:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM ATTACHMENT WHERE attachment_id = %s", (attachment_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row if row else {}

    def find_all_by_slot(self, slot_type: str) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM ATTACHMENT WHERE slot_type = %s ORDER BY attachment_name",
            (slot_type,)
        )

    def update(self, df: pd.DataFrame):
        sql = """
            UPDATE ATTACHMENT
            SET attachment_name=%s, slot_type=%s, image_data=%s,
                control_recoil_vertical=%s, control_recoil_horizontal=%s,
                control_muzzle_rise=%s, control_muzzle_shake=%s,
                mod_recovery_recoil=%s, control_first_recoil=%s
            WHERE attachment_id = %s
        """
        for _, r in df.iterrows():
            self._run(sql, (
                r['attachment_name'], r['slot_type'], r['image_data'],
                r['control_recoil_vertical'], r['control_recoil_horizontal'],
                r['control_muzzle_rise'], r['control_muzzle_shake'],
                r['mod_recovery_recoil'], r['control_first_recoil'],
                r['attachment_id']
            ))

    def delete_by_id(self, attachment_id: int) -> bool:
        self._run(
            "DELETE FROM ATTACHMENT WHERE attachment_id = %s", (attachment_id,)
        )
        return True


class WeaponAttachmentCompatRepository(IWeaponAttachmentCompatRepository):

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
            INSERT INTO WEAPON_ATTACHMENT_COMPAT
                (compat_id, weapon_id, attachment_id,
                 control_recoil_vertical, control_recoil_horizontal,
                 control_muzzle_rise, control_muzzle_shake,
                 mod_recovery_recoil, control_first_recoil)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                control_recoil_vertical=%s, control_recoil_horizontal=%s,
                control_muzzle_rise=%s, control_muzzle_shake=%s,
                mod_recovery_recoil=%s, control_first_recoil=%s
        """
        for _, r in df.iterrows():
            v = (r['compat_id'], r['weapon_id'], r['attachment_id'],
                 r['control_recoil_vertical'], r['control_recoil_horizontal'],
                 r['control_muzzle_rise'], r['control_muzzle_shake'],
                 r['mod_recovery_recoil'], r['control_first_recoil'],
                 r['control_recoil_vertical'], r['control_recoil_horizontal'],
                 r['control_muzzle_rise'], r['control_muzzle_shake'],
                 r['mod_recovery_recoil'], r['control_first_recoil'])
            self._run(sql, v)

    def find_all_by_weapon_id(self, weapon_id: int) -> pd.DataFrame:
        return self._df(
            "SELECT * FROM WEAPON_ATTACHMENT_COMPAT WHERE weapon_id = %s",
            (weapon_id,)
        )

    def find_by_weapon_and_attachment(self, weapon_id: int, attachment_id: int) -> dict:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM WEAPON_ATTACHMENT_COMPAT WHERE weapon_id = %s AND attachment_id = %s",
            (weapon_id, attachment_id)
        )
        row = cursor.fetchone()
        cursor.close()
        return row if row else {}

    def delete_by_id(self, compat_id: int) -> bool:
        self._run(
            "DELETE FROM WEAPON_ATTACHMENT_COMPAT WHERE compat_id = %s", (compat_id,)
        )
        return True
