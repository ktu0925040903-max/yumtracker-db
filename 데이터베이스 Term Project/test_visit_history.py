import flet as ft
import duckdb

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 통합 방문 이력 조회"
    page.window_width = 750
    page.window_height = 900
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

    # 2. 사용자 입력 및 필터링 제어 컴포넌트
    search_restaurant_input = ft.TextField(
        label="조회할 식당 고유 ID (공백 시 전체 조회)", 
        hint_text="예: 1", 
        width=300
    )

    sort_dropdown = ft.Dropdown(
        label="정렬 조건 선택",
        width=300,
        options=[
            ft.dropdown.Option("latest", "📅 최신순 (방문 날짜순)"),
            ft.dropdown.Option("rating_high", "⭐ 별점 높은 순"),
            ft.dropdown.Option("price_low", "💰 가격 낮은 순")
        ],
        value="latest"
    )

    # 방문 기록이 출력될 동적 컨테이너 리스트
    history_list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=500)

    # 3. 데이터베이스 조회 및 동적 정렬 로직
    def load_visit_history(e=None):
        history_list_container.controls.clear()
        
        try:
            conn = duckdb.connect("yumtracker.db")
            
            # 방어적 테이블 생성
            conn.execute("""
                CREATE TABLE IF NOT EXISTS local_visit_logs (
                    log_id INTEGER, restaurant_id INTEGER, menu_id INTEGER, 
                    visit_date VARCHAR, amount_spent INTEGER, rating INTEGER, revisit VARCHAR
                )
            """)

            # 정렬 조건 분기
            sort_type = sort_dropdown.value
            if sort_type == "latest":
                order_by_clause = "ORDER BY visit_date DESC"
            elif sort_type == "rating_high":
                order_by_clause = "ORDER BY rating DESC"
            elif sort_type == "price_low":
                order_by_clause = "ORDER BY amount_spent ASC"
            else:
                order_by_clause = "ORDER BY log_id DESC"

            # 사용자 입력 식당 ID 조건에 따른 동적 WHERE 절 구성
            search_val = search_restaurant_input.value.strip()
            if search_val:
                query = f"""
                    SELECT log_id, visit_date, amount_spent, rating, revisit 
                    FROM local_visit_logs 
                    WHERE restaurant_id = ?
                    {order_by_clause}
                """
                logs = conn.execute(query, [int(search_val)]).fetchall()
            else:
                query = f"""
                    SELECT log_id, visit_date, amount_spent, rating, revisit 
                    FROM local_visit_logs 
                    {order_by_clause}
                """
                logs = conn.execute(query).fetchall()
                
            conn.close()

            # 유효한 카운트를 체크하기 위한 변수
            visible_card_count = 0

            if not logs:
                history_list_container.controls.append(
                    ft.Text("조회 조건에 부합하는 방문 기록이 존재하지 않는다.", size=16, color="grey")
                )
            else:
                for row in logs:
                    # 💡 [핵심 변경 사항] 금액 데이터가 없거나 0원이면 아래 UI 생성 코드를 건너뛰고 다음 데이터로 넘어간다 (continue)
                    if row[2] is None or row[2] == 0:
                        continue
                    
                    # 0원이 아닌 유효 데이터가 존재하므로 카운트를 증가시킴
                    visible_card_count += 1
                    
                    visit_date = row[1] if row[1] is not None else "날짜 미기입"
                    amount = f"{row[2]:,}원"
                    stars = "⭐" * row[3] if row[3] else "별점 없음"
                    revisit_status = "💡 재방문 의사 있음" if row[4] == "Y" else "❌ 재방문 의사 없음"
                    
                    log_card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"📅 날짜: {visit_date}", size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(f"금액: {amount}", size=14, color="#2E7D32")
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text(f"평점: {stars}", size=14),
                                ft.Text(revisit_status, size=13, color="blue")
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ]),
                        padding=15, bgcolor="#FFFFFF", border_radius=8, border=ft.Border.all(1, "#E0E0E0")
                    )
                    history_list_container.controls.append(log_card)
                
                # 만약 데이터는 조회되었으나 전부 0원이라서 화면에 뜬 카드가 하나도 없다면 안내 문구를 띄운다
                if visible_card_count == 0:
                    history_list_container.controls.append(
                        ft.Text("유효한 금액 정보를 가진 방문 기록이 존재하지 않음.", size=16, color="grey")
                    )
                    
        except Exception as err:
            history_list_container.controls.append(
                ft.Text(f"❌ 데이터 로드 실패 (오류: {err})", color="red")
            )
            
        page.update()

    sort_dropdown.on_change = load_visit_history
    
    search_button = ft.ElevatedButton(
        content=ft.Text("조회하기", color="white"),
        bgcolor="#1A237E",
        on_click=load_visit_history
    )

    view_container = ft.Container(
        content=ft.Column([
            ft.Text("📊 나의 방문 히스토리 검색", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                search_restaurant_input,
                sort_dropdown,
                search_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            history_list_container
        ]),
        padding=20, bgcolor="#F8F9FA", border_radius=10, border=ft.Border.all(1, "#DEE2E6")
    )

    load_visit_history()
    page.add(top_navigation_bar, ft.Divider(), view_container)

ft.app(target=main)