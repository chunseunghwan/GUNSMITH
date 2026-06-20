import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
from repository.i_attachment_repository import IAttachmentRepository
from repository.I_weapon_attachment_compat_repository import IWeaponAttachmentCompatRepository
from database import Database


class AttachmentRepository(IAttachmentRepository):

    def __init__(self, db: Database):
        self.db = db

    def save(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "INSERT OR REPLACE INTO ATTACHMENT VALUES (?,?,?,?)", list(r)
            )

    def find_all(self) -> pd.DataFrame:
        return self.db.q("SELECT * FROM ATTACHMENT ORDER BY slot_type, attachment_name")

    def find_by_id(self, attachment_id: int) -> dict:
        df = self.db.q("SELECT * FROM ATTACHMENT WHERE attachment_id=?", [attachment_id])
        return df.iloc[0].to_dict() if not df.empty else {}

    def find_all_by_slot(self, slot_type: str) -> pd.DataFrame:
        return self.db.q(
            "SELECT * FROM ATTACHMENT WHERE slot_type=? ORDER BY attachment_name",
            [slot_type]
        )

    def update(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "UPDATE ATTACHMENT SET attachment_name=?, slot_type=?, image_data=? WHERE attachment_id=?",
                [r['attachment_name'], r['slot_type'], r['image_data'], r['attachment_id']]
            )

    def delete_by_id(self, attachment_id: int) -> bool:
        self.db.run("DELETE FROM ATTACHMENT WHERE attachment_id=?", [attachment_id])
        return True


class WeaponAttachmentCompatRepository(IWeaponAttachmentCompatRepository):

    def __init__(self, db: Database):
        self.db = db

    def save(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "INSERT OR REPLACE INTO WEAPON_ATTACHMENT_COMPAT VALUES (?,?,?,?,?,?,?,?,?)",
                list(r)
            )

    def find_all_by_weapon_id(self, weapon_id: int) -> pd.DataFrame:
        return self.db.q(
            "SELECT * FROM WEAPON_ATTACHMENT_COMPAT WHERE weapon_id=?", [weapon_id]
        )

    def find_by_weapon_and_attachment(self, weapon_id: int, attachment_id: int) -> dict:
        df = self.db.q(
            "SELECT * FROM WEAPON_ATTACHMENT_COMPAT WHERE weapon_id=? AND attachment_id=?",
            [weapon_id, attachment_id]
        )
        return df.iloc[0].to_dict() if not df.empty else {}

    def find_by_weapon_and_slot(self, weapon_id: int, slot_type: str) -> pd.DataFrame:
        """3-way JOIN: WEAPON + WEAPON_ATTACHMENT_COMPAT + ATTACHMENT"""
        return self.db.q("""
            SELECT a.attachment_id, a.attachment_name, a.slot_type, a.image_data,
                   c.control_recoil_vertical, c.control_recoil_horizontal,
                   c.control_muzzle_rise, c.control_muzzle_shake,
                   c.mod_recovery_recoil, c.control_first_recoil
            FROM WEAPON w
            JOIN WEAPON_ATTACHMENT_COMPAT c ON w.weapon_id = c.weapon_id
            JOIN ATTACHMENT a ON c.attachment_id = a.attachment_id
            WHERE w.weapon_id = ? AND a.slot_type = ?
            ORDER BY a.attachment_name
        """, [weapon_id, slot_type])

    def delete_by_id(self, compat_id: int) -> bool:
        self.db.run("DELETE FROM WEAPON_ATTACHMENT_COMPAT WHERE compat_id=?", [compat_id])
        return True
