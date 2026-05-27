from abc import ABC, abstractmethod
import pandas as pd

class ICustomConfigRepository(ABC):

    @abstractmethod
    def save(self, df: pd.DataFrame):
        """커스텀 설정 저장 (CREATE)"""
        pass

    @abstractmethod
    def find_all(self) -> pd.DataFrame:
        """전체 커스텀 설정 목록 조회 (READ)"""
        pass

    @abstractmethod
    def find_by_id(self, config_id: int) -> dict:
        """config_id로 커스텀 설정 단건 조회 (READ)"""
        pass

    @abstractmethod
    def find_all_by_weapon_id(self, weapon_id: int) -> pd.DataFrame:
        """weapon_id로 해당 총기의 커스텀 목록 조회 (READ)"""
        pass

    @abstractmethod
    def update(self, df: pd.DataFrame):
        """커스텀 설정 수정 (UPDATE)"""
        pass

    @abstractmethod
    def delete_by_id(self, config_id: int) -> bool:
        """커스텀 설정 삭제 (DELETE)"""
        pass