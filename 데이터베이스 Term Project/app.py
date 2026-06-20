import flet as ft
import duckdb
import os

def main(page: ft.Page):
    # ==========================================
    # [1] 애플리케이션 초기화 및 창 환경 설정
    # ==========================================
    page.title = "YumTracker v1.0"
    page.window_width = 750
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # ==========================================
    # [2] 상단 네비게이션 바 컴포넌트 정의
    # ==========================================
    top_navigation_bar = ft.Row(
        controls=[
            # 프로젝트 시스템 타이틀 출력
            ft.Text("YumTracker v1.0", size=24, weight=ft.FontWeight.BOLD, color="#1A237E"),
            ft.VerticalDivider(width=20),
            # 시스템 유스케이스 이동 버튼 배치
            ft.TextButton("마이 대시보드"),
            ft.TextButton("식당 등록"),
            ft.TextButton("방문 기록 관리")
        ]
    )

    # ==========================================
    # [3] 중앙 영역: Pandas 데이터 분석 및 통계 차트 (미구현 대체 컴포넌트)
    # ==========================================
    center_stats_area = ft.Container(
        content=ft.Column([
            ft.Text("📊 통계 대시보드 (데이터 분석 영역)", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("※ 카테고리별 누적 지출 및 맵기 비율 차트는 스키마 확장 후 구현 예정 (현재 미구현)", size=12, color="grey")
        ]),
        padding=15,
        # 버전에 무관하게 크로스 컴파일 에러를 방지하는 표준 명시적 Border 객체 선언
        border=ft.Border(
            top=ft.BorderSide(1, "#E0E0E0"), 
            bottom=ft.BorderSide(1, "#E0E0E0"), 
            left=ft.BorderSide(1, "#E0E0E0"), 
            right=ft.BorderSide(1, "#E0E0E0")
        ),
        border_radius=8
    )

    # ==========================================
    # [4] 하단 영역: 실시간 추천 맛집 카드 컴포넌트 정의
    # ==========================================
    recommendation_title = ft.Text("⭐ 실시간 추천 맛집", size=18, weight=ft.FontWeight.BOLD)
    recommendation_list = ft.Column(spacing=10)

    # ==========================================
    # [5] 백엔드 DuckDB 연동 및 데이터 처리 로직 함수
    # ==========================================
    def load_dashboard_data():
        # 컨테이너 초기화
        recommendation_list.controls.clear()
        try:
            # 로컬 DuckDB 인스턴스 파일 커넥션 확보
            conn = duckdb.connect("yumtracker.db")
            
            # [핵심 쿼리] 방문기록(l), 식당(r), 시그니처 메뉴(m) 테이블을 INNER JOIN 연산 처리
            # 사용자의 평점(l.rating)이 가장 높은 데이터 기준 역순 정렬 후 상위 2개만 추출 (LIMIT 2)
            query = """
            SELECT r.name, m.menu_name, l.rating, r.image_path 
            FROM local_visit_logs l 
            JOIN my_restaurants r ON l.restaurant_id = r.restaurant_id 
            JOIN signature_menu m ON l.menu_id = m.menu_id 
            ORDER BY l.rating DESC 
            LIMIT 2
            """
            data = conn.execute(query).fetchall()
            conn.close()

            # 데이터 바인딩 루프 실행
            for row in data:
                # 로컬 이미지 파일 경로 유효성 검사 및 예외 방지 예외 처리
                img_path = row[3] if row[3] and os.path.exists(row[3]) else ""
                
                # 가로 정렬(ft.Row) 구조 내부에 이미지와 서술 텍스트 배정
                recommendation_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            # 꼬임 오류 방지를 위한 정적 호출 인스턴스 컴포넌트 매핑
                            ft.Image(src=img_path, width=100, height=100, fit=ft.ImageFit.COVER, border_radius=8),
                            ft.Column([
                                ft.Text(f"식당: {row[0]}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"메뉴: {row[1]}"),
                                ft.Text(f"평점: {row[2]} / 5", color="#FFB300")
                            ])
                        ]),
                        padding=10,
                        bgcolor="#F5F7FA",
                        border_radius=10,
                        border=ft.Border(
                            top=ft.BorderSide(1, "#CFD8DC"), 
                            bottom=ft.BorderSide(1, "#CFD8DC"), 
                            left=ft.BorderSide(1, "#CFD8DC"), 
                            right=ft.BorderSide(1, "#CFD8DC")
                        )
                    )
                )
        except Exception as e:
            # 데이터베이스 유실 혹은 런타임 크래시 발생 시 UI 먹통 방지용 에러 메시지 렌더링
            recommendation_list.controls.append(ft.Text(f"오류: {e}", color="red"))
        page.update()

    # 페이지 초기 구동 시 백엔드 핸들러 즉시 동기화 실행
    load_dashboard_data()
    
    # ==========================================
    # [6] 메인 레이아웃 트리에 컴포넌트 추가 및 갱신
    # ==========================================
    page.add(top_navigation_bar, ft.Divider(), center_stats_area, recommendation_title, recommendation_list)

# 애플리케이션 진입점 선언
ft.app(target=main)