from abc import ABC, abstractmethod
import pandas as pd

class IWeaponRepository(ABC):

    @abstractmethod
    def save(self, df: pd.DataFrame):
        """총기 정보 저장 (CREATE)"""
        pass

    @abstractmethod
    def find_all(self) -> pd.DataFrame:
        """전체 총기 목록 조회 (READ)"""
        pass

    @abstractmethod
    def find_by_id(self, weapon_id: int) -> dict:
        """weapon_id로 총기 단건 조회 (READ)"""
        pass

    @abstractmethod
    def find_all_by_type(self, gun_type: str) -> pd.DataFrame:
        """총기 종류별 목록 조회 (READ) - AR/SMG/DMR 등 필터링"""
        pass

    @abstractmethod
    def find_by_keyword(self, keyword: str) -> pd.DataFrame:
        """총기 이름 키워드 검색 (READ)"""
        pass

    @abstractmethod
    def update(self, df: pd.DataFrame):
        """총기 정보 수정 (UPDATE)"""
        pass

    @abstractmethod
    def delete_by_id(self, weapon_id: int) -> bool:
        """총기 삭제 (DELETE)"""
        pass
    