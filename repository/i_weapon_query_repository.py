from abc import ABC, abstractmethod
import pandas as pd

class IWeaponQueryRepository(ABC):

    @abstractmethod
    def find_weapon_with_recoil(self, weapon_id: int) -> dict:
        """
        WEAPON + WEAPON_RECOIL Join
        총기 조회 시 상세 반동 수치를 함께 조회 (READ)
        """
        pass

    @abstractmethod
    def find_compat_parts_by_weapon(self, weapon_id: int) -> pd.DataFrame:
        """
        WEAPON + WEAPON_ATTACHMENT_COMPAT + ATTACHMENT 3-way Join
        총기에 장착 가능한 파츠 목록과 총기별 보정값 조회 (READ)
        """
        pass

    @abstractmethod
    def find_compare_results(self, config_id_left: int, config_id_right: int) -> pd.DataFrame:
        """
        CUSTOM_CONFIG + RECOIL_RESULT Join
        두 커스텀 설정의 최종 반동 수치 비교 조회 (READ)
        """
        pass