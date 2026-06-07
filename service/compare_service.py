import pandas as pd


class CompareService:

    def __init__(self, query_repo, config_repo, result_repo):
        self.query_repo = query_repo
        self.config_repo = config_repo
        self.result_repo = result_repo

    def get_all_configs(self) -> pd.DataFrame:
        return self.config_repo.find_all_with_weapon_name()

    def get_compare_data(self, config_id_left: int, config_id_right: int) -> pd.DataFrame:
        """CUSTOM_CONFIG LEFT JOIN RECOIL_RESULT 비교 데이터 반환"""
        return self.query_repo.find_compare_results(config_id_left, config_id_right)
