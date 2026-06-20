import flet as ft
import duckdb
import os

def main(page: ft.Page):
    page.title = "YumTracker v1.0 - 맛집 상세 조회"
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
            ft.TextButton("식당 관리"), 
            ft.TextButton("방문 기록 관리")
        ]
    )

    # 2. 결과 리스트 및 상세 정보 영역 정의
    restaurant_list = ft.Column(spacing=10, height=300, scroll=ft.ScrollMode.AUTO)
    detail_view = ft.Container(
        content=ft.Text("식당을 선택하면 상세 정보가 여기에 표시됩니다.", color="grey"),
        padding=20,
        bgcolor="#E8EAF6",
        border_radius=10,
        width=700
    )

    # 3. 상세 정보 출력 함수 (식당 클릭 시 실행)
    def show_detail(e, name):
        detail_view.content = ft.Column([
            ft.Text(f"🏠 {name} 상세 정보", size=20, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.Divider(),
            ft.Text(f"가져온 식당 이름: {name}"),
            ft.Text("상세 설명: 본 식당은 DuckDB에 등록된 맛집으로, 뛰어난 맛과 서비스를 자랑합니다."),
            ft.Text("추가 정보: 주차 가능 / 단체석 완비 / 예약 권장", size=13, color="blue")
        ])
        page.update()

    # 4. 데이터베이스에서 목록 불러오기
    def load_restaurants():
        restaurant_list.controls.clear()
        conn = duckdb.connect("yumtracker.db")
        data = conn.execute("SELECT name, address, image_path FROM my_restaurants").fetchall()
        conn.close()

        for row in data:
            name_val = row[0]
            img_path = row[2] if row[2] and os.path.exists(row[2]) else ""
            
            # 조건: 원하는 식당을 클릭한다 (on_click 이벤트 추가)
            restaurant_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Image(src=img_path, width=60, height=60, border_radius=5),
                        ft.Column([
                            ft.Text(name_val, weight=ft.FontWeight.BOLD),
                            ft.Text(f"주소: {row[1]}", size=12)
                        ])
                    ]),
                    padding=10,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.Border(top=ft.BorderSide(1, "#CFD8DC"), bottom=ft.BorderSide(1, "#CFD8DC"), left=ft.BorderSide(1, "#CFD8DC"), right=ft.BorderSide(1, "#CFD8DC")),
                    on_click=lambda e, n=name_val: show_detail(e, n) # 클릭 이벤트
                )
            )
        page.update()

    load_restaurants() # 시작 시 목록 로드

    # 화면 구성
    page.add(
        top_navigation_bar,
        ft.Divider(),
        ft.Text("📋 식당 목록 (클릭 시 상세 조회)", size=16, weight=ft.FontWeight.BOLD),
        restaurant_list,
        ft.Text("📍 상세 정보 결과", size=16, weight=ft.FontWeight.BOLD),
        detail_view
    )

ft.app(target=main)