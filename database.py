import duckdb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "GUNSMITH_DB.duckdb")


class Database:
    """DuckDB 싱글톤 연결 래퍼"""
    _instance = None

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = duckdb.connect(db_path or DB_PATH)
        return cls._instance

    def q(self, sql: str, params=None):
        """SELECT → DataFrame 반환"""
        if params:
            return self.conn.execute(sql, params).df()
        return self.conn.execute(sql).df()

    def run(self, sql: str, params=None):
        """INSERT / UPDATE / DELETE / DDL 실행"""
        if params:
            self.conn.execute(sql, params)
        else:
            self.conn.execute(sql)

    def scalar(self, sql: str, params=None):
        """단일 스칼라 값 반환"""
        row = self.conn.execute(sql, params).fetchone() if params else self.conn.execute(sql).fetchone()
        return row[0] if row else None

    def close(self):
        if self.conn:
            self.conn.close()
        Database._instance = None
