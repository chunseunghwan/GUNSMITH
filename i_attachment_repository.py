from abc import ABC, abstractmethod
import pandas as pd
class IAttachmentRepository(ABC):

    @abstractmethod
    def save(self, df: pd.DataFrame):
        """파츠 정보 저장 (CREATE)"""
        pass

    @abstractmethod
    def find_all(self) -> pd.DataFrame:
        """전체 파츠 목록 조회 (READ)"""
        pass

    @abstractmethod
    def find_by_id(self, attachment_id: int) -> dict:
        """attachment_id로 파츠 단건 조회 (READ)"""
        pass

    @abstractmethod
    def find_all_by_slot(self, slot_type: str) -> pd.DataFrame:
        """슬롯 타입별 파츠 목록 조회 (READ) - Muzzle/Stock/Grip 등 필터링"""
        pass

    @abstractmethod
    def update(self, df: pd.DataFrame):
        """파츠 정보 수정 (UPDATE)"""
        pass

    @abstractmethod
    def delete_by_id(self, attachment_id: int) -> bool:
        """파츠 삭제 (DELETE)"""
        pass