import flet as ft
import duckdb
import os

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 맛집 조회"
    page.window_width = 750
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 상단 네비게이션 바
    top_navigation_bar = ft.Row(
        controls=[
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            ft.TextButton("마이 대시보드"),
            ft.TextButton("식당 관리"), 
            ft.TextButton("방문 기록 관리")
        ]
    )

    # 2. 검색창 및 카테고리 필터 영역
    search_input = ft.TextField(label="식당 이름 검색", width=300, hint_text="검색어를 입력하세요")
    
    category_dropdown = ft.Dropdown(
        label="카테고리 선택",
        width=200,
        options=[
            ft.dropdown.Option("전체"),
            ft.dropdown.Option("한식"),
            ft.dropdown.Option("중식"),
            ft.dropdown.Option("일식"),
            ft.dropdown.Option("양식")
        ],
        value="전체"
    )
    
    # 💡 오류 원천 차단: 내부 속성(text) 대신 content 구조를 사용하여 버전을 타지 않도록 빌드
    search_button = ft.ElevatedButton(
        content=ft.Text("검색", color="white"), 
        bgcolor="#1A237E"
    )

    # 필터 영역 가로 배치
    filter_area = ft.Row(
        controls=[search_input, category_dropdown, search_button],
        spacing=10
    )

    # 3. 결과 출력 영역
    restaurant_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    # 4. 데이터베이스 조회 로직 
    def search_restaurants(e):
        restaurant_list.controls.clear()
        
        keyword = f"%{search_input.value}%"
        selected_category = category_dropdown.value

        conn = duckdb.connect("yumtracker.db")
        
        query = "SELECT name, category, address, image_path FROM my_restaurants WHERE name LIKE ?"
        params = [keyword]

        if selected_category != "전체":
            query += " AND category = ?"
            params.append(selected_category)

        data = conn.execute(query, params).fetchall()
        conn.close()

        for row in data:
            img_path = row[3] if row[3] and os.path.exists(row[3]) else ""
            
            restaurant_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Image(src=img_path, width=80, height=80, border_radius=5),
                        ft.Column([
                            ft.Text(f"식당명: {row[0]}", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"카테고리: {row[1]}", size=13, color="blue"),
                            ft.Text(f"주소: {row[2]}", size=13)
                        ])
                    ]),
                    padding=10,
                    bgcolor="#F5F7FA",
                    border_radius=8,
                    border=ft.Border(top=ft.BorderSide(1, "#CFD8DC"), bottom=ft.BorderSide(1, "#CFD8DC"), left=ft.BorderSide(1, "#CFD8DC"), right=ft.BorderSide(1, "#CFD8DC"))
                )
            )
        page.update()

    # 버튼에 함수 연결
    search_button.on_click = search_restaurants

    # 최초 실행 시 전체 목록 출력
    search_restaurants(None)

    # 화면 컴포넌트 배치
    page.add(
        top_navigation_bar, 
        ft.Divider(), 
        filter_area, 
        ft.Text("🔍 검색 결과", size=16, weight=ft.FontWeight.BOLD), 
        restaurant_list
    )

ft.app(target=main)