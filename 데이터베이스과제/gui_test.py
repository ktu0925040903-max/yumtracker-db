import flet as ft
import duckdb

def main(page: ft.Page):
    # 1. 페이지 설정
    page.title = "맛집 데이터베이스 조회 시스템"
    page.window_width = 600
    page.window_height = 500
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    # 제목
    title = ft.Text("내 맛집 DB JOIN 결과 조회", size=25, weight=ft.FontWeight.BOLD)

    # 결과를 출력할 리스트 뷰
    results_view = ft.Column(spacing=10)

    def load_data(e):
        results_view.controls.clear()
        try:
            # 2. DB 연결 및 JOIN 쿼리 실행
            conn = duckdb.connect("yumtracker.db")
            join_query = """
            SELECT r.name, m.menu_name, l.rating 
            FROM local_visit_logs l
            JOIN my_restaurants r ON l.restaurant_id = r.restaurant_id
            JOIN signature_menu m ON l.menu_id = m.menu_id
            """
            data = conn.execute(join_query).fetchall()
            conn.close()

            # 3. 데이터를 화면에 추가
            if not data:
                results_view.controls.append(ft.Text("데이터가 없습니다. 먼저 test_run.py를 실행하세요."))
            else:
                for row in data:
                    results_view.controls.append(
                        ft.Container(
                            content=ft.Text(f"🏠 식당: {row[0]}  |  🍴 메뉴: {row[1]}  |  ⭐ 평점: {row[2]}점", size=16),
                            padding=10,
                            bgcolor="#E3F2FD",  # <--- 에러를 일으키던 ft.colors 대신 안전한 헥사 코드로 변경했습니다.
                            border_radius=10
                        )
                    )
        except Exception as ex:
            results_view.controls.append(ft.Text(f"에러 발생: {ex}", color="red"))
        
        page.update()

    result_col = ft.Column()

    def load_data(e):
        result_col.controls.clear()
        try:
            conn = duckdb.connect("yumtracker.db")
            data = conn.execute("SELECT name, menu_name, rating, image_path FROM local_visit_logs l JOIN my_restaurants r ON l.restaurant_id = r.restaurant_id JOIN signature_menu m ON l.menu_id = m.menu_id").fetchall()
            conn.close()

            for row in data:
                # 여기서 Image를 별도 설정 없이 src 하나만으로 간단하게 호출합니다.
                result_col.controls.append(
                    ft.Row([
                        ft.Image(src=row[3], width=100, height=100),
                        ft.Text(f"{row[0]} / {row[1]} / {row[2]}점")
                    ])
                )
        except Exception as ex:
            result_col.controls.append(ft.Text(str(ex)))
        page.update()

    page.add(ft.ElevatedButton("조회", on_click=load_data), result_col)

    # 조회 버튼
    btn = ft.ElevatedButton("DB 데이터 불러오기 (3개 테이블 JOIN)", on_click=load_data, icon="refresh")

    # 화면 구성
    page.add(
        title,
        ft.Divider(),
        btn,
        ft.Text("\n[조회 결과]"),
        results_view
    )

# 앱 실행
ft.app(target=main)
