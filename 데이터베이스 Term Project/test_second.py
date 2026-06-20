import flet as ft
import duckdb
import os

def main(page: ft.Page):
    page.title = "YumTracker v1.0"
    page.window_width = 750
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # 1. 상단 네비게이션
    top_navigation_bar = ft.Row(
        controls=[
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            ft.TextButton("마이 대시보드"),
            ft.TextButton("식당 등록"),
            ft.TextButton("방문 기록 관리")
        ]
    )

    # 2. 중앙 영역
    center_stats_area = ft.Container(
        content=ft.Column([
            ft.Text("📊 통계 대시보드 (데이터 분석 영역)", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("※ 차트는 스키마 확장 후 구현 예정", size=12, color="grey")
        ]),
        padding=15,
        border=ft.Border(top=ft.BorderSide(1, "#E0E0E0"), bottom=ft.BorderSide(1, "#E0E0E0"), left=ft.BorderSide(1, "#E0E0E0"), right=ft.BorderSide(1, "#E0E0E0")),
        border_radius=8
    )

    recommendation_title = ft.Text("⭐ 실시간 추천 맛집", size=18, weight=ft.FontWeight.BOLD)
    recommendation_list = ft.Column(spacing=10)

    # 3. 데이터 로드 로직 (ImageFit 속성 완전 제거)
    def load_dashboard_data():
        recommendation_list.controls.clear()
        try:
            conn = duckdb.connect("yumtracker.db")
            query = "SELECT r.name, m.menu_name, l.rating, r.image_path FROM local_visit_logs l JOIN my_restaurants r ON l.restaurant_id = r.restaurant_id JOIN signature_menu m ON l.menu_id = m.menu_id ORDER BY l.rating DESC LIMIT 2"
            data = conn.execute(query).fetchall()
            conn.close()

            for row in data:
                img_path = row[3] if row[3] and os.path.exists(row[3]) else ""
                
                recommendation_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            # 💡 fit 속성을 제거하여 오류 가능성을 완벽히 차단했습니다!
                            ft.Image(src=img_path, width=100, height=100, border_radius=8),
                            ft.Column([
                                ft.Text(f"식당: {row[0]}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"메뉴: {row[1]}"),
                                ft.Text(f"평점: {row[2]} / 5", color="#FFB300"),
                                ft.Text(f"🖼️ 이미지 경로: {img_path if img_path else '기본 대체 이미지'}", size=11, color="grey")
                            ])
                        ]),
                        padding=10,
                        bgcolor="#F5F7FA",
                        border_radius=10,
                        border=ft.Border(top=ft.BorderSide(1, "#CFD8DC"), bottom=ft.BorderSide(1, "#CFD8DC"), left=ft.BorderSide(1, "#CFD8DC"), right=ft.BorderSide(1, "#CFD8DC"))
                    )
                )
        except Exception as e:
            recommendation_list.controls.append(ft.Text(f"오류: {e}", color="red"))
        page.update()

    load_dashboard_data()
    page.add(top_navigation_bar, ft.Divider(), center_stats_area, recommendation_title, recommendation_list)

ft.app(target=main)