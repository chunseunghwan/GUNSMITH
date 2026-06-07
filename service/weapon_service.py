import pandas as pd


class WeaponService:

    def __init__(self, weapon_repo, weapon_recoil_repo, query_repo):
        self.weapon_repo = weapon_repo
        self.weapon_recoil_repo = weapon_recoil_repo
        self.query_repo = query_repo

    def get_all(self) -> pd.DataFrame:
        return self.query_repo.find_all_weapons_with_grade()

    def get_by_type(self, gun_type: str) -> pd.DataFrame:
        return self.query_repo.find_weapons_by_type(gun_type)

    def get_with_recoil(self, weapon_id: int) -> dict:
        return self.query_repo.find_weapon_with_recoil(weapon_id)

    def get_compat_parts(self, weapon_id: int) -> pd.DataFrame:
        return self.query_repo.find_compat_parts_by_weapon(weapon_id)
