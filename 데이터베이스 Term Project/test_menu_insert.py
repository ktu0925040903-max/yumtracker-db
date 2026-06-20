import flet as ft
import duckdb

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 시그니처 메뉴 등록"
    page.window_width = 750
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 상단 네비게이션 바
    top_navigation_bar = ft.Row(
        controls=[
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            ft.TextButton("마이 대시보드"),
            ft.TextButton("식당 관리"), 
            ft.TextButton("대표 메뉴 등록") 
        ]
    )

    # 2. 식당 정보 및 메뉴 입력 폼
    restaurant_id_input = ft.TextField(label="연결할 식당 고유 ID (숫자)", width=500)
    menu_name_input = ft.TextField(label="시그니처 메뉴 이름", width=500)
    
    # 💡 추가된 항목: 가격 입력
    price_input = ft.TextField(label="가격 (숫자만)", hint_text="예: 12000", width=500)
    
    # 💡 추가된 항목: 맵기 단계 선택
    spiciness_dropdown = ft.Dropdown(
        label="맵기 단계 (0~3단계)",
        width=500,
        options=[
            ft.dropdown.Option("0"), ft.dropdown.Option("1"),
            ft.dropdown.Option("2"), ft.dropdown.Option("3")
        ],
        value="0"
    )
    
    status_message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    # 3. 데이터베이스 저장 로직
    def register_signature_menu(e):
        if not restaurant_id_input.value or not menu_name_input.value or not price_input.value:
            status_message.value = "❌ 모든 항목을 입력해주세요."
            status_message.color = "red"
            page.update()
            return

        try:
            conn = duckdb.connect("yumtracker.db")
            
            # 🛠️ [중요] 테이블에 컬럼이 없을 경우를 대비해 컬럼을 강제로 추가하는 명령 (에러 방지)
            try:
                conn.execute("ALTER TABLE signature_menu ADD COLUMN price INTEGER")
            except: pass # 이미 있으면 무시
            try:
                conn.execute("ALTER TABLE signature_menu ADD COLUMN spiciness INTEGER")
            except: pass # 이미 있으면 무시

            # 데이터 삽입
            query = """
                INSERT INTO signature_menu (menu_id, restaurant_id, menu_name, price, spiciness) 
                VALUES (
                    (SELECT COALESCE(MAX(menu_id), 0) + 1 FROM signature_menu), 
                    ?, ?, ?, ?
                )
            """
            conn.execute(query, [
                int(restaurant_id_input.value), 
                menu_name_input.value, 
                int(price_input.value), 
                int(spiciness_dropdown.value)
            ])
            conn.commit()
            conn.close()

            status_message.value = f"🎉 '{menu_name_input.value}' 메뉴 등록 성공!"
            status_message.color = "green"
            
            # 입력란 초기화
            restaurant_id_input.value = ""
            menu_name_input.value = ""
            price_input.value = ""
            spiciness_dropdown.value = "0"
            
        except Exception as err:
            status_message.value = f"❌ 등록 실패 (오류: {err})"
            status_message.color = "red"
            
        page.update()

    submit_button = ft.ElevatedButton(
        content=ft.Text("메뉴 등록하기", color="white"),
        bgcolor="#1A237E", width=200,
        on_click=register_signature_menu
    )

    form_container = ft.Container(
        content=ft.Column([
            ft.Text("🍴 시그니처 메뉴 정보 입력", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            restaurant_id_input,
            menu_name_input,
            price_input,
            spiciness_dropdown,
            ft.Divider(height=10, color="transparent"),
            submit_button,
            status_message
        ], spacing=15),
        padding=20, bgcolor="#F8F9FA", border_radius=10, border=ft.Border.all(1, "#DEE2E6")
    )

    page.add(top_navigation_bar, ft.Divider(), form_container)

ft.app(target=main)