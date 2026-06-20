import duckdb

class DuckDBConnection:
    def __init__(self, db_name="yumtracker.db"):
        self.db_name = db_name
        self.conn = duckdb.connect(self.db_name)

    def execute_query(self, query, params=()):
       # 쿼리를 실행하는 공통 함수
        return self.conn.execute(query, params)

    def close(self):
        self.conn.close()