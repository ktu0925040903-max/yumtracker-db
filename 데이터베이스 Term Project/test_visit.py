import flet as ft
import duckdb

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 방문 기록 생성"
    page.window_width = 750
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 상단 네비게이션 바
    top_navigation_bar = ft.Row(
        controls=[
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            ft.TextButton("마이 대시보드"),
            ft.TextButton("식당 관리"), 
            ft.TextButton("방문 로그 작성")
        ]
    )

    # 2. 방문 기록 입력 폼 컴포넌트 정의
    restaurant_id_input = ft.TextField(label="식당 고유 ID (숫자)", hint_text="예: 1", width=500)
    menu_id_input = ft.TextField(label="선택한 메뉴 고유 ID (숫자)", hint_text="예: 3", width=500)
    visit_date_input = ft.TextField(label="방문 날짜", hint_text="예: 2026-06-20", width=500)
    amount_spent_input = ft.TextField(label="지출 금액 (숫자만)", hint_text="예: 15000", width=500)
    
    rating_dropdown = ft.Dropdown(
        label="부여할 별점",
        width=500,
        options=[
            ft.dropdown.Option("5", "⭐⭐⭐⭐⭐"),
            ft.dropdown.Option("4", "⭐⭐⭐⭐"),
            ft.dropdown.Option("3", "⭐⭐⭐"),
            ft.dropdown.Option("2", "⭐⭐"),
            ft.dropdown.Option("1", "⭐")
        ],
        value="5"
    )
    
    revisit_checkbox = ft.Checkbox(label="다음에 다시 방문하시겠습니까? (재방문 의사 있음)", value=True)
    status_message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    # 3. 데이터베이스 저장 로직
    def register_visit_log(e):
        if not restaurant_id_input.value or not menu_id_input.value or not visit_date_input.value or not amount_spent_input.value:
            status_message.value = "❌ 필수 항목을 모두 입력해주세요."
            status_message.color = "red"
            page.update()
            return

        try:
            conn = duckdb.connect("yumtracker.db")
            
            # 테이블이 아예 없는 경우를 대비한 생성
            conn.execute("""
                CREATE TABLE IF NOT EXISTS local_visit_logs (
                    log_id INTEGER, restaurant_id INTEGER
                )
            """)
            
            # 🛠️ [중요] 테이블은 있으나 특정 컬럼이 누락된 경우를 대비해 컬럼 강제 추가 (에러 원천 방지)
            columns_to_add = {
                "menu_id": "INTEGER",
                "visit_date": "VARCHAR",
                "amount_spent": "INTEGER",
                "rating": "INTEGER",
                "revisit": "VARCHAR"
            }
            
            for col_name, col_type in columns_to_add.items():
                try:
                    conn.execute(f"ALTER TABLE local_visit_logs ADD COLUMN {col_name} {col_type}")
                except:
                    pass # 이미 컬럼이 존재하면 에러를 무시하고 진행

            revisit_value = "Y" if revisit_checkbox.value else "N"

            # 레코드 삽입 쿼리 실행
            query = """
                INSERT INTO local_visit_logs (log_id, restaurant_id, menu_id, visit_date, amount_spent, rating, revisit) 
                VALUES (
                    (SELECT COALESCE(MAX(log_id), 0) + 1 FROM local_visit_logs), 
                    ?, ?, ?, ?, ?, ?
                )
            """
            conn.execute(query, [
                int(restaurant_id_input.value),
                int(menu_id_input.value),
                visit_date_input.value,
                int(amount_spent_input.value),
                int(rating_dropdown.value),
                revisit_value
            ])
            conn.commit()
            conn.close()

            status_message.value = "🎉 방문 기록이 성공적으로 저장되었습니다!"
            status_message.color = "green"
            
            # 입력란 초기화
            restaurant_id_input.value = ""
            menu_id_input.value = ""
            visit_date_input.value = ""
            amount_spent_input.value = ""
            rating_dropdown.value = "5"
            revisit_checkbox.value = True
            
        except Exception as err:
            status_message.value = f"❌ 저장 실패 (오류: {err})"
            status_message.color = "red"
            
        page.update()

    submit_button = ft.ElevatedButton(
        content=ft.Text("방문 로그 저장하기", color="white"),
        bgcolor="#1A237E", width=200,
        on_click=register_visit_log
    )

    form_container = ft.Container(
        content=ft.Column([
            ft.Text("📝 맛집 방문 기록 입력", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            restaurant_id_input,
            menu_id_input,
            visit_date_input,
            amount_spent_input,
            rating_dropdown,
            ft.Row([revisit_checkbox], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=10, color="transparent"),
            submit_button,
            status_message
        ], spacing=15),
        padding=20, bgcolor="#F8F9FA", border_radius=10, border=ft.Border.all(1, "#DEE2E6")
    )

    page.add(top_navigation_bar, ft.Divider(), form_container)

ft.app(target=main)