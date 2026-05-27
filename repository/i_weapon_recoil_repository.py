from abc import ABC, abstractmethod
import pandas as pd
class IWeaponRecoilRepository(ABC):

    @abstractmethod
    def save(self, df: pd.DataFrame):
        """총기 반동 스탯 저장 (CREATE)"""
        pass

    @abstractmethod
    def find_by_weapon_id(self, weapon_id: int) -> dict:
        """weapon_id로 반동 스탯 단건 조회 (READ)"""
        pass

    @abstractmethod
    def update(self, df: pd.DataFrame):
        """반동 스탯 수정 (UPDATE)"""
        pass

    @abstractmethod
    def delete_by_weapon_id(self, weapon_id: int) -> bool:
        """반동 스탯 삭제 (DELETE)"""
        pass