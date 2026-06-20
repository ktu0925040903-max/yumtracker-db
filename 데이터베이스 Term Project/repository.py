from database import DuckDBConnection
import pandas as pd

class RestaurantRepository:
    def __init__(self):
        self.db = DuckDBConnection()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS my_restaurants (
            restaurant_id INTEGER PRIMARY KEY,
            name VARCHAR,
            category VARCHAR,
            address VARCHAR,
            image_path VARCHAR
        )
        """
        self.db.execute_query(query)

    def count(self):
        result = self.db.execute_query("SELECT COUNT(*) FROM my_restaurants").fetchone()
        return result[0]

    def save(self, name, category, address, image_path):
        query = "INSERT INTO my_restaurants (name, category, address, image_path) VALUES (?, ?, ?, ?)"
        self.db.execute_query(query, (name, category, address, image_path))
        print(f"'{name}' 식당 저장 완료!")

    def find_all(self):
        result = self.db.execute_query("SELECT * FROM my_restaurants").fetchall()
        return result
def create_table(self):
        # 1. Entity: 식당 테이블
        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS my_restaurants (
            restaurant_id INTEGER PRIMARY KEY,
            name VARCHAR,
            category VARCHAR
        )""")
        
        # 2. Entity: 메뉴 테이블
        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS signature_menu (
            menu_id INTEGER PRIMARY KEY,
            restaurant_id INTEGER,
            menu_name VARCHAR
        )""")
        
        # 3. Relationship: 방문 기록 테이블
        self.db.execute_query("""
        CREATE TABLE IF NOT EXISTS local_visit_logs (
            log_id INTEGER PRIMARY KEY,
            restaurant_id INTEGER,
            visit_date DATE,
            rating INTEGER
        )""")
        print("3개 테이블 생성 완료!")