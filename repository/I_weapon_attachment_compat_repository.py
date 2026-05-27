from abc import ABC, abstractmethod
import pandas as pd

class IWeaponAttachmentCompatRepository(ABC):

    @abstractmethod
    def save(self, df: pd.DataFrame):
        """총기-파츠 호환 정보 저장 (CREATE)"""
        pass

    @abstractmethod
    def find_all_by_weapon_id(self, weapon_id: int) -> pd.DataFrame:
        """weapon_id로 장착 가능한 파츠 목록 조회 (READ)"""
        pass

    @abstractmethod
    def find_by_weapon_and_attachment(self, weapon_id: int, attachment_id: int) -> dict:
        """특정 총기-파츠 호환 여부 단건 조회 (READ)"""
        pass

    @abstractmethod
    def delete_by_id(self, compat_id: int) -> bool:
        """호환 정보 삭제 (DELETE)"""
        pass