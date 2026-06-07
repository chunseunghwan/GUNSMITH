import pandas as pd


class AttachmentService:

    def __init__(self, attachment_repo, compat_repo):
        self.attachment_repo = attachment_repo
        self.compat_repo = compat_repo

    def get_all(self) -> pd.DataFrame:
        return self.attachment_repo.find_all()

    def get_by_slot(self, slot_type: str) -> pd.DataFrame:
        return self.attachment_repo.find_all_by_slot(slot_type)

    def get_compat_by_weapon(self, weapon_id: int) -> pd.DataFrame:
        return self.compat_repo.find_all_by_weapon_id(weapon_id)

    def get_compat_by_weapon_and_slot(self, weapon_id: int, slot_type: str) -> pd.DataFrame:
        return self.compat_repo.find_by_weapon_and_slot(weapon_id, slot_type)
