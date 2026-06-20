import flet as ft
import duckdb
import pandas as pd

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 마이 대시보드"
    page.window_width = 800
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 상단 네비게이션 바
    top_navigation_bar = ft.Row(
        controls=[
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            ft.TextButton("마이 대시보드"),
            ft.TextButton("나의 방문 기록"),
            ft.TextButton("식당 관리")
        ]
    )

    # 차트가 표시될 컨테이너
    chart_container = ft.Column(spacing=20, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # 2. 데이터 분석 및 차트 생성 로직
    def load_dashboard_data():
        chart_container.controls.clear()
        
        try:
            conn = duckdb.connect("yumtracker.db")
            
            # 방어적 테이블 생성
            conn.execute("CREATE TABLE IF NOT EXISTS restaurants (restaurant_id INTEGER, category VARCHAR)")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS local_visit_logs (
                    log_id INTEGER, restaurant_id INTEGER, menu_id INTEGER, 
                    visit_date VARCHAR, amount_spent INTEGER, rating INTEGER, revisit VARCHAR
                )
            """)
            
            # 중복 에러를 방지하며 안전하게 카테고리 매핑 테이블 데이터 삽입
            conn.execute("INSERT INTO restaurants SELECT 1, '한식' WHERE NOT EXISTS (SELECT 1 FROM restaurants WHERE restaurant_id = 1)")
            conn.execute("INSERT INTO restaurants SELECT 2, '일식' WHERE NOT EXISTS (SELECT 1 FROM restaurants WHERE restaurant_id = 2)")
            conn.execute("INSERT INTO restaurants SELECT 3, '중식' WHERE NOT EXISTS (SELECT 1 FROM restaurants WHERE restaurant_id = 3)")
            conn.execute("INSERT INTO restaurants SELECT 4, '양식' WHERE NOT EXISTS (SELECT 1 FROM restaurants WHERE restaurant_id = 4)")
            conn.execute("INSERT INTO restaurants SELECT 5, '카페/디저트' WHERE NOT EXISTS (SELECT 1 FROM restaurants WHERE restaurant_id = 5)")
            
            # log_id 제약조건 통과를 위해 임의의 일련번호를 포함한 전체 컬럼 데이터 삽입
            count = conn.execute("SELECT COUNT(*) FROM local_visit_logs").fetchone()[0]
            if count < 5:
                conn.execute("""
                    INSERT INTO local_visit_logs (log_id, restaurant_id, menu_id, visit_date, amount_spent, rating, revisit) 
                    VALUES 
                    (101, 1, 1, '2026-06-01', 15000, 5, 'Y'),
                    (102, 1, 2, '2026-06-02', 28000, 4, 'Y'),
                    (103, 1, 3, '2026-06-03', 42000, 5, 'Y'),
                    (104, 2, 1, '2026-06-04', 35000, 4, 'Y'),
                    (105, 2, 2, '2026-06-05', 55000, 5, 'N'),
                    (106, 3, 1, '2026-06-06', 12000, 3, 'Y'),
                    (107, 3, 2, '2026-06-07', 22000, 4, 'N'),
                    (108, 4, 1, '2026-06-08', 45000, 5, 'Y'),
                    (109, 4, 2, '2026-06-09', 68000, 4, 'Y'),
                    (110, 5, 1, '2026-06-10', 8000, 5, 'Y'),
                    (111, 5, 2, '2026-06-11', 9500, 4, 'N')
                """)
            
            # 관계형 데이터 결합 조회
            query = """
                SELECT r.category, l.amount_spent 
                FROM local_visit_logs l
                JOIN restaurants r ON l.restaurant_id = r.restaurant_id
            """
            raw_data = conn.execute(query).fetchall()
            conn.close()

            if not raw_data:
                chart_container.controls.append(ft.Text("지출 데이터가 존재하지 않는다.", size=16, color="grey"))
                page.update()
                return

            # Pandas 파이프라인 데이터 가공
            df = pd.DataFrame(raw_data, columns=['category', 'amount_spent'])
            stats = df.groupby('category')['amount_spent'].sum().reset_index().sort_values(by='amount_spent', ascending=False)
            max_spent = stats['amount_spent'].max()

            # 가로형 바 차트 UI 빌드
            for _, row in stats.iterrows():
                category = row['category']
                amount = row['amount_spent']
                bar_width = (amount / max_spent) * 400 if max_spent > 0 else 0

                chart_container.controls.append(
                    ft.Column([
                        ft.Row([
                            ft.Text(category, size=16, weight=ft.FontWeight.W_500, width=100),
                            ft.Container(
                                content=ft.Text(f"{amount:,}원", color="white", size=12, weight=ft.FontWeight.BOLD),
                                bgcolor="#3F51B5",
                                border_radius=5,
                                padding=ft.Padding(left=10, right=10, top=0, bottom=0),
                                width=bar_width + 80,
                                height=30,
                                # 💡 [수정] 대문자 Alignment 객체 명세를 사용하여 정렬 속성 에러 해결
                                alignment=ft.Alignment(1, 0), 
                            )
                        ], alignment=ft.MainAxisAlignment.START)
                    ])
                )
                
        except Exception as err:
            chart_container.controls.append(ft.Text(f"❌ 분석 실패: {err}", color="red"))
            
        page.update()

    # 대시보드 레이아웃 구성
    dashboard_view = ft.Container(
        content=ft.Column([
            ft.Text("📊 카테고리별 누적 지출 통계", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("최근 방문 기록을 바탕으로 분석된 소비 성향이다.", size=14, color="grey"),
            ft.Divider(height=30),
            chart_container,
            ft.Divider(height=30),
            ft.ElevatedButton("데이터 새로고침", icon="refresh", on_click=lambda _: load_dashboard_data())
        ]),
        padding=30, bgcolor="#F8F9FA", border_radius=15, border=ft.Border.all(1, "#DEE2E6")
    )

    load_dashboard_data()
    page.add(top_navigation_bar, ft.Divider(), dashboard_view)

ft.app(target=main)