import flet as ft
import duckdb

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 맛집 등록"
    page.window_width = 750
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 상단 네비게이션 바
    top_navigation_bar = ft.Row(
        controls=[
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            ft.TextButton("마이 대시보드"),
            ft.TextButton("새 식당 등록"), # 조건: 메뉴 탭에서 '새 식당 등록'을 클릭한다
            ft.TextButton("방문 기록 관리")
        ]
    )

    # 2. 식당 등록 폼 컴포넌트 정의 (조건: 식당 이름, 카테고리, 주소, 로컬 이미지 경로 입력)
    name_input = ft.TextField(label="식당 이름", hint_text="예: 할머니 국밥", width=500)
    
    category_dropdown = ft.Dropdown(
        label="카테고리",
        width=500,
        options=[
            ft.dropdown.Option("한식"),
            ft.dropdown.Option("중식"),
            ft.dropdown.Option("일식"),
            ft.dropdown.Option("양식")
        ]
    )
    
    address_input = ft.TextField(label="주소", hint_text="예: 서울시 강남구 역삼동 123", width=500)
    image_path_input = ft.TextField(label="로컬 이미지 경로", hint_text="예: gukbap.jpg", width=500)
    
    # 결과 알림 텍스트
    status_message = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    # 3. 데이터베이스 저장 로직 (조건: 입력된 정보가 데이터베이스 테이블에 저장된다)
    def register_restaurant(e):
        # 입력값 누락 검사
        if not name_input.value or not category_dropdown.value or not address_input.value:
            status_message.value = "❌ 필수 입력 항목(식당 이름, 카테고리, 주소)을 모두 채워주세요."
            status_message.color = "red"
            page.update()
            return

        try:
            conn = duckdb.connect("yumtracker.db")
            
            # 레코드 삽입 쿼리문 실행 (restaurant_id는 자동 생성이 아닐 경우를 대비해 최댓값 + 1 처리 등으로 유연하게 대처 가능하나, 여기서는 표준 구조 유지)
            # 시스템 환경에 따라 ID 컬럼이 필수일 수 있으므로 안전하게 서브쿼리로 ID 부여
            query = """
                INSERT INTO my_restaurants (restaurant_id, name, category, address, image_path) 
                VALUES (
                    (SELECT COALESCE(MAX(restaurant_id), 0) + 1 FROM my_restaurants), 
                    ?, ?, ?, ?
                )
            """
            conn.execute(query, [name_input.value, category_dropdown.value, address_input.value, image_path_input.value])
            conn.commit()
            conn.close()

            # 저장 성공 시 폼 초기화 및 알림
            status_message.value = f"🎉 '{name_input.value}' 식당이 성공적으로 등록되었습니다!"
            status_message.color = "green"
            
            name_input.value = ""
            category_dropdown.value = None
            address_input.value = ""
            image_path_input.value = ""
            
        except Exception as err:
            status_message.value = f"❌ 등록 실패 (오류: {err})"
            status_message.color = "red"
            
        page.update()

    # 등록 버튼 생성
    submit_button = ft.ElevatedButton(
        content=ft.Text("식당 등록하기", color="white"),
        bgcolor="#1A237E",
        width=200,
        on_click=register_restaurant
    )

    # 폼 레이아웃 구획화
    form_container = ft.Container(
        content=ft.Column([
            ft.Text("📝 식당 정보 입력", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            name_input,
            category_dropdown,
            address_input,
            image_path_input,
            ft.Divider(height=10, color="transparent"),
            submit_button,
            status_message
        ], spacing=15),
        padding=20,
        bgcolor="#F5F7FA",
        border_radius=10,
        border=ft.Border.all(1, "#CFD8DC")
    )

    # 화면에 컴포넌트 배치
    page.add(
        top_navigation_bar,
        ft.Divider(),
        form_container
    )

ft.app(target=main)