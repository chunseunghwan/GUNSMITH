from abc import ABC, abstractmethod
import pandas as pd

class IRecoilResultRepository(ABC):

    @abstractmethod
    def save(self, df: pd.DataFrame):
        """반동 계산 결과 저장 (CREATE)"""
        pass

    @abstractmethod
    def find_by_config_id(self, config_id: int) -> dict:
        """config_id로 반동 결과 단건 조회 (READ)"""
        pass

    @abstractmethod
    def update(self, df: pd.DataFrame):
        """반동 결과 수정 (UPDATE)"""
        pass

    @abstractmethod
    def delete_by_config_id(self, config_id: int) -> bool:
        """반동 결과 삭제 (DELETE)"""
        pass