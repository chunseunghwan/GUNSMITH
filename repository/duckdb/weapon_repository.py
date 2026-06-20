import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import pandas as pd
from repository.i_weapon_repository import IWeaponRepository
from repository.i_weapon_recoil_repository import IWeaponRecoilRepository
from database import Database


class WeaponRepository(IWeaponRepository):

    def __init__(self, db: Database):
        self.db = db

    def save(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "INSERT OR REPLACE INTO WEAPON VALUES (?,?,?,?,?,?,?,?,?,?)",
                list(r)
            )

    def find_all(self) -> pd.DataFrame:
        return self.db.q("SELECT * FROM WEAPON ORDER BY gun_type, weapon_name")

    def find_by_id(self, weapon_id: int) -> dict:
        df = self.db.q("SELECT * FROM WEAPON WHERE weapon_id=?", [weapon_id])
        return df.iloc[0].to_dict() if not df.empty else {}

    def find_all_by_type(self, gun_type: str) -> pd.DataFrame:
        return self.db.q(
            "SELECT * FROM WEAPON WHERE gun_type=? ORDER BY weapon_name", [gun_type]
        )

    def find_by_keyword(self, keyword: str) -> pd.DataFrame:
        return self.db.q(
            "SELECT * FROM WEAPON WHERE weapon_name ILIKE ? ORDER BY weapon_name",
            [f"%{keyword}%"]
        )

    def update(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                """UPDATE WEAPON SET weapon_name=?, gun_type=?, bullet_type=?, damage=?,
                   bullet_speed=?, fire_speed=?, description=?, is_custom=?, image_data=?
                   WHERE weapon_id=?""",
                [r['weapon_name'], r['gun_type'], r['bullet_type'], r['damage'],
                 r['bullet_speed'], r['fire_speed'], r['description'], r['is_custom'],
                 r['image_data'], r['weapon_id']]
            )

    def delete_by_id(self, weapon_id: int) -> bool:
        self.db.run("DELETE FROM WEAPON WHERE weapon_id=?", [weapon_id])
        return True


class WeaponRecoilRepository(IWeaponRecoilRepository):

    def __init__(self, db: Database):
        self.db = db

    def save(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                "INSERT OR REPLACE INTO WEAPON_RECOIL VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                list(r)
            )

    def find_by_weapon_id(self, weapon_id: int) -> dict:
        df = self.db.q("SELECT * FROM WEAPON_RECOIL WHERE weapon_id=?", [weapon_id])
        return df.iloc[0].to_dict() if not df.empty else {}

    def update(self, df: pd.DataFrame):
        for _, r in df.iterrows():
            self.db.run(
                """UPDATE WEAPON_RECOIL SET recoil_vertical=?, recoil_horizontal=?,
                   pattern_scale=?, first_recoil=?, crouch_modifier=?, prone_modifier=?,
                   muzzle_rise=?, muzzle_shake=?, recovery_recoil=?, vertical_speed=?,
                   stability_score=?, stability_grade=? WHERE weapon_id=?""",
                [r['recoil_vertical'], r['recoil_horizontal'], r['pattern_scale'],
                 r['first_recoil'], r['crouch_modifier'], r['prone_modifier'],
                 r['muzzle_rise'], r['muzzle_shake'], r['recovery_recoil'],
                 r['vertical_speed'], r['stability_score'], r['stability_grade'],
                 r['weapon_id']]
            )

    def delete_by_weapon_id(self, weapon_id: int) -> bool:
        self.db.run("DELETE FROM WEAPON_RECOIL WHERE weapon_id=?", [weapon_id])
        return True
