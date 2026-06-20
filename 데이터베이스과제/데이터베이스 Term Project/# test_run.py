import duckdb

# 1. DB 파일 연결 및 초기화
conn = duckdb.connect("yumtracker.db")

print("=== (1) SQL 기반 3개 테이블 생성 시작 ===")
# 에러 방지를 위해 기존 테이블 삭제
conn.execute("DROP TABLE IF EXISTS local_visit_logs")
conn.execute("DROP TABLE IF EXISTS signature_menu")
conn.execute("DROP TABLE IF EXISTS my_restaurants")

# [Entity 1] 식당 테이블
conn.execute("""
CREATE TABLE my_restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    name VARCHAR,
    category VARCHAR,
    address VARCHAR,
    image_path VARCHAR
)""")

# [Entity 2] 대표 메뉴 테이블
conn.execute("""
CREATE TABLE signature_menu (
    menu_id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    menu_name VARCHAR
)""")

# [Relationship] 방문 기록 테이블
conn.execute("""
CREATE TABLE local_visit_logs (
    log_id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    menu_id INTEGER,
    visit_date DATE,
    rating INTEGER
)""")
print("👉 3개 테이블 생성 완료!\n")


print("=== (2) 관계형 데이터 삽입 (INSERT) ===")
conn.execute("INSERT INTO my_restaurants VALUES (1, '할머니 국밥', '한식', '서울 종로구', 'gukbap.jpg')")
conn.execute("INSERT INTO signature_menu VALUES (101, 1, '따로국밥')")
conn.execute("INSERT INTO local_visit_logs VALUES (501, 1, 101, '2026-06-20', 5)")
print("👉 데이터 삽입 성공!\n")


print("=== (3) 최종 데이터 조회 결과 (증빙용) ===")
# 문제의 구간을 안전하게 분리해서 작성했습니다.
res_restaurant = conn.execute("SELECT * FROM my_restaurants").fetchall()
res_menu = conn.execute("SELECT * FROM signature_menu").fetchall()
res_log = conn.execute("SELECT * FROM local_visit_logs").fetchall()

print("식당 테이블:", res_restaurant)
print("메뉴 테이블:", res_menu)
print("방문 로그:", res_log)

print("\n=== (4) 3개 테이블 JOIN 연산 결과  ===")
join_query = """
SELECT r.name AS 식당이름, m.menu_name AS 대표메뉴, l.rating AS 평점
FROM local_visit_logs l
JOIN my_restaurants r ON l.restaurant_id = r.restaurant_id
JOIN signature_menu m ON l.menu_id = m.menu_id
"""
res_join = conn.execute(join_query).fetchall()
print("JOIN 결과:", res_join)

conn.close()
print("\n=== 모든 프로세스가 정상적으로 종료되었습니다 ===")