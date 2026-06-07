import flet as ft

BG    = "#0d1117"
CARD  = "#161b27"
CARD2 = "#1e2535"
ACCENT = "#4fc3f7"
TEXT  = "#dde3ed"
DIM   = "#6b7585"

SLOT_COLOR = {
    'Muzzle':   '#4fc3f7',
    'Stock':    '#66BB6A',
    'Grip':     '#FFD700',
    'Magazine': '#ff9800',
    'Scope':    '#e91e63',
    'Foregrip': '#ab47bc',
}
SLOT_KR = {
    'Muzzle': '총구', 'Stock': '개머리판', 'Grip': '손잡이',
    'Magazine': '탄창', 'Scope': '조준경', 'Foregrip': '전술손잡이',
}


def build_attachment_view(page: ft.Page, attachment_service) -> ft.Control:
    list_col   = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=3)
    detail_col = ft.Column(
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=8,
        controls=[ft.Text("← 파츠를 클릭하면 상세 정보가 표시됩니다.", color=DIM, size=13)],
    )

    def load_list(slot_type=None):
        df = attachment_service.get_by_slot(slot_type) if slot_type and slot_type != '전체' \
             else attachment_service.get_all()

        rows = []
        for _, r in df.iterrows():
            slot = r.get('slot_type','')
            sc = SLOT_COLOR.get(slot, DIM)
            rows.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(r['attachment_name'], color=TEXT, size=13,
                                        weight=ft.FontWeight.W_600),
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(SLOT_KR.get(slot, slot), color="#0d1117",
                                        size=10, weight=ft.FontWeight.BOLD),
                        bgcolor=sc, padding=ft.Padding(left=0, right=0, top=0, bottom=0), border_radius=8,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=CARD,
                padding=ft.Padding(left=14, right=14, top=9, bottom=9),
                border_radius=6,
                border=ft.Border.all(1, "#252d3f"),
                on_click=lambda e, row=r.to_dict(): show_detail(row),
                ink=True,
            ))

        list_col.controls = rows
        try:
            list_col.update()
        except Exception:
            pass

    def show_detail(r: dict):
        slot = r.get('slot_type','')
        sc = SLOT_COLOR.get(slot, DIM)

        def bonus_row(label, val, invert=True):
            v = float(val or 0)
            if v == 0:
                c, sym = DIM, '  —'
            elif v < 0:
                c, sym = '#66BB6A', f'  ▼ {abs(v):.4f}  (감소↓)'
            else:
                c, sym = '#ff5252', f'  ▲ {v:.4f}  (증가↑)'
            return ft.Row([
                ft.Text(label, color=DIM, size=12, width=160),
                ft.Text(sym, color=c, size=12),
            ])

        detail_col.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Image(
                        src=r.get('image_path',''),
                        width=140, height=90, fit=ft.BoxFit.CONTAIN,
                        error_content=ft.Container(
                            width=140, height=90, bgcolor=CARD2, border_radius=8,
                            content=ft.Text(r['attachment_name'], color=sc,
                                            text_align=ft.TextAlign.CENTER, size=11),
                            alignment=ft.Alignment.CENTER,
                        ),
                    ),
                    ft.Column([
                        ft.Text(r['attachment_name'], color=TEXT, size=18,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(
                                SLOT_KR.get(slot, slot) + "  슬롯",
                                color="#0d1117", size=11, weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=sc, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                            border_radius=10,
                        ),
                    ], spacing=8, expand=True),
                ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("■  반동 보정값  (음수 = 개선)", color=ACCENT,
                            size=13, weight=ft.FontWeight.BOLD),
                    ft.Text("※ 실제 수치는 총기별 호환 테이블(WEAPON_ATTACHMENT_COMPAT)에 따라 상이",
                            color=DIM, size=10),
                    bonus_row("수직 반동 보정",   r.get('control_recoil_vertical')),
                    bonus_row("좌우 반동 보정",   r.get('control_recoil_horizontal')),
                    bonus_row("총구 들림 보정",   r.get('control_muzzle_rise')),
                    bonus_row("총구 흔들림 보정", r.get('control_muzzle_shake')),
                    bonus_row("초탄 반동 보정",   r.get('control_first_recoil')),
                    bonus_row("반동 회복 보정",   r.get('mod_recovery_recoil')),
                ], spacing=7),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),
        ]
        detail_col.update()

    slot_dd = ft.Dropdown(
        value='전체',
        options=[ft.dropdown.Option(s) for s in
                 ['전체', 'Muzzle', 'Stock', 'Grip', 'Magazine', 'Scope']],
        on_select=lambda e: load_list(e.control.value),
        bgcolor=CARD2, color=TEXT, border_color=ACCENT, width=150, text_size=13,
    )

    header_row = ft.Container(
        content=ft.Row([
            ft.Text("파츠명", color=DIM, size=11, weight=ft.FontWeight.BOLD, expand=True),
            ft.Text("슬롯",   color=DIM, size=11, width=80),
        ]),
        padding=ft.Padding(left=14, right=14, top=5, bottom=5),
        border=ft.Border(bottom=ft.BorderSide(1, "#252d3f")),
    )

    load_list()

    return ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("슬롯 필터:", color=TEXT, size=13),
                    slot_dd,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                header_row,
                list_col,
            ], spacing=6, expand=True),
            width=380,
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            border=ft.Border(right=ft.BorderSide(1, "#252d3f")),
        ),
        ft.Container(content=detail_col, expand=True, padding=20),
    ], expand=True)



