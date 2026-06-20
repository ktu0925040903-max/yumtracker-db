def load_signature_menu(e, restaurant_id, restaurant_name):
        menu_display_area.controls.clear()
        signature_menu_section.visible = True
        
        conn = duckdb.connect("yumtracker.db")
        # 💡 spiciness 대신 실제 DB 컬럼명인 spicy로 수정
        query = "SELECT menu_name, spicy FROM signature_menu WHERE restaurant_id = ?"
        menus = conn.execute(query, [restaurant_id]).fetchall()
        conn.close()

        if not menus:
            menu_display_area.controls.append(ft.Text("등록된 대표 메뉴가 없습니다.", color="grey"))
        else:
            for m in menus:
                # m[1]에 저장된 맵기 숫자로 고추 아이콘 생성
                spice_icons = "🌶️" * int(m[1]) if m[1] else "안매움"
                
                menu_display_area.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.RESTAURANT_MENU, color="#1A237E"),
                            ft.Column([
                                ft.Text(f"{m[0]}", size=16, weight=ft.FontWeight.BOLD),
                                ft.Row([
                                    ft.Text(f"맵기: {spice_icons}", size=14, color="#D32F2F"),
                                ])
                            ], spacing=2)
                        ]),
                        padding=10,
                        bgcolor="white",
                        border_radius=10,
                    )
                )
        page.update()