import flet as ft

BG    = "#0d1117"
CARD  = "#161b27"
CARD2 = "#1e2535"
ACCENT = "#4fc3f7"
TEXT  = "#dde3ed"
DIM   = "#6b7585"
RED   = "#ff5252"
GRADE_COLOR = {'S': '#FFD700', 'A': '#4fc3f7', 'B': '#66BB6A', 'C': '#FF7043'}


def _grade_chip(grade):
    c = GRADE_COLOR.get(str(grade), DIM)
    return ft.Container(
        content=ft.Text(str(grade), color="#0d1117", size=11, weight=ft.FontWeight.BOLD),
        bgcolor=c, padding=ft.Padding(left=0, right=0, top=0, bottom=0), border_radius=8,
    )


def _label(text, value, unit='', val_color=TEXT):
    return ft.Row([
        ft.Text(text, color=DIM, size=12, width=150),
        ft.Text(f"{value}{unit}", color=val_color, size=13, weight=ft.FontWeight.W_500),
    ], spacing=4)


def _recoil_bar(label, value, max_val=12.0):
    v = float(value or 0)
    pct = min(v / max_val, 1.0)
    return ft.Column([
        ft.Row([
            ft.Text(label, color=DIM, size=11, width=130),
            ft.Text(f"{v:.4f}", color=TEXT, size=11),
        ], spacing=6),
        ft.ProgressBar(value=pct, bgcolor="#252d3f", color="#ff6b6b", height=5, border_radius=3),
    ], spacing=2)


def build_weapon_view(page: ft.Page, weapon_service) -> ft.Control:
    list_col   = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=3)
    detail_col = ft.Column(
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=8,
        controls=[ft.Text("← 좌측에서 총기를 클릭하면 상세 정보가 표시됩니다.", color=DIM, size=13)],
    )

    # ── 목록 로드 ─────────────────────────────────────────────────
    def load_list(gun_type=None):
        df = weapon_service.get_by_type(gun_type) if gun_type and gun_type != '전체' \
             else weapon_service.get_all()

        rows = []
        for _, r in df.iterrows():
            grade = str(r.get('stability_grade') or '?')
            gc = GRADE_COLOR.get(grade, DIM)
            rows.append(ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(r['weapon_name'], color=TEXT, size=13,
                                        weight=ft.FontWeight.W_600),
                        expand=True,
                    ),
                    ft.Text(r['gun_type'] or '', color=ACCENT, size=11, width=48),
                    ft.Text(r['bullet_type'] or '', color=DIM, size=11, width=52),
                    ft.Text(str(r['damage'] or '-'), color=RED, size=11, width=36,
                            text_align=ft.TextAlign.RIGHT),
                    ft.Container(width=8),
                    _grade_chip(grade),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=CARD,
                padding=ft.Padding(left=14, right=14, top=9, bottom=9),
                border_radius=6,
                border=ft.Border.all(1, "#252d3f"),
                on_click=lambda e, wid=int(r['weapon_id']): show_detail(wid),
                ink=True,
            ))

        list_col.controls = rows
        try:
            list_col.update()
        except Exception:
            pass

    # ── 상세 정보 ──────────────────────────────────────────────────
    def show_detail(weapon_id: int):
        data = weapon_service.get_with_recoil(weapon_id)
        if not data:
            return
        w = data['weapon']
        r = data['recoil']

        grade = str(r.get('stability_grade') or '?')
        score = int(r.get('stability_score') or 0)
        gc = GRADE_COLOR.get(grade, DIM)

        img = ft.Image(
            src=w.get('image_path', ''),
            width=200, height=110, fit=ft.BoxFit.CONTAIN,
            error_content=ft.Container(
                width=200, height=110, bgcolor=CARD2, border_radius=8,
                content=ft.Text(w['weapon_name'], color=ACCENT,
                                text_align=ft.TextAlign.CENTER, size=14),
                alignment=ft.Alignment.CENTER,
            ),
        )

        detail_col.controls = [
            # 헤더 ─────────────────────────────────────
            ft.Container(
                content=ft.Row([
                    img,
                    ft.Column([
                        ft.Text(w['weapon_name'], color=ACCENT, size=22,
                                weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(w.get('gun_type',''), color="#0d1117",
                                                size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=ACCENT, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                                border_radius=10,
                            ),
                            ft.Container(
                                content=ft.Text(f"등급  {grade}", color="#0d1117",
                                                size=12, weight=ft.FontWeight.BOLD),
                                bgcolor=gc, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                                border_radius=10,
                            ),
                        ], spacing=6),
                        ft.Text(w.get('description',''), color=DIM, size=11, max_lines=3),
                        ft.Text(
                            '✓ 파츠 커스텀 가능' if w.get('is_custom') else '✗ 파츠 커스텀 불가',
                            color='#66BB6A' if w.get('is_custom') else RED, size=11,
                        ),
                    ], spacing=6, expand=True),
                ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.START),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),

            # 기본 제원 ────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("■  기본 제원", color=ACCENT, size=13, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Column([
                            _label("탄약 종류",   w.get('bullet_type', '-')),
                            _label("발당 피해량", w.get('damage', '-'), ' dmg', RED),
                            _label("탄속",       w.get('bullet_speed', '-'), ' m/s'),
                        ], expand=True, spacing=6),
                        ft.Column([
                            _label("연사속도",  w.get('fire_speed', '-'), ' RPM'),
                            _label("총기 종류", w.get('gun_type', '-')),
                        ], expand=True, spacing=6),
                    ]),
                ], spacing=8),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),

            # 반동 스탯 ────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("■  반동 스탯  (단위: 10px / FHD 1920×1080)",
                            color=ACCENT, size=13, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Column([
                            _recoil_bar("수직 반동",   r.get('recoil_vertical')),
                            _recoil_bar("좌우 반동",   r.get('recoil_horizontal'), 6.0),
                            _recoil_bar("초탄 반동",   r.get('first_recoil')),
                        ], expand=True, spacing=7),
                        ft.Column([
                            _recoil_bar("총구 들림",   r.get('muzzle_rise')),
                            _recoil_bar("총구 흔들림", r.get('muzzle_shake'), 6.0),
                            _recoil_bar("반동 회복",   r.get('recovery_recoil'), 6.0),
                        ], expand=True, spacing=7),
                    ], spacing=20),
                    ft.Row([
                        ft.Text("앉아쏴 배율:", color=DIM, size=11),
                        ft.Text(f"×{r.get('crouch_modifier', '-')}", color=TEXT, size=11),
                        ft.Container(width=20),
                        ft.Text("엎드려쏴 배율:", color=DIM, size=11),
                        ft.Text(f"×{r.get('prone_modifier', '-')}", color=TEXT, size=11),
                    ], spacing=4),
                ], spacing=10),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),

            # 안정성 ───────────────────────────────────
            ft.Container(
                content=ft.Column([
                    ft.Text("■  안정성", color=ACCENT, size=13, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text(f"{score}", color=gc, size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("/ 100", color=DIM, size=18),
                        ft.Container(width=10),
                        ft.Container(
                            content=ft.Text(f"등급  {grade}", color="#0d1117",
                                            size=16, weight=ft.FontWeight.BOLD),
                            bgcolor=gc, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                            border_radius=12,
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.BASELINE),
                    ft.ProgressBar(
                        value=score / 100, bgcolor="#252d3f", color=gc,
                        height=16, border_radius=8,
                    ),
                ], spacing=8),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),
        ]
        detail_col.update()

    # ── 필터 드롭다운 ─────────────────────────────────────────────
    type_dd = ft.Dropdown(
        value='전체',
        options=[ft.dropdown.Option(t) for t in
                 ['전체', 'AR', 'SMG', 'DMR', 'LMG', 'SR', 'SG', 'Pistol']],
        on_select=lambda e: load_list(e.control.value),
        bgcolor=CARD2, color=TEXT, border_color=ACCENT, width=130, text_size=13,
    )

    header_row = ft.Container(
        content=ft.Row([
            ft.Text("총기명", color=DIM, size=11, weight=ft.FontWeight.BOLD, expand=True),
            ft.Text("종류", color=DIM, size=11, width=48),
            ft.Text("탄약", color=DIM, size=11, width=52),
            ft.Text("피해", color=DIM, size=11, width=36, text_align=ft.TextAlign.RIGHT),
            ft.Container(width=8),
            ft.Text("등급", color=DIM, size=11, width=32),
        ]),
        padding=ft.Padding(left=14, right=14, top=5, bottom=5),
        border=ft.Border(bottom=ft.BorderSide(1, "#252d3f")),
    )

    load_list()

    return ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("종류 필터:", color=TEXT, size=13),
                    type_dd,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                header_row,
                list_col,
            ], spacing=6, expand=True),
            width=420,
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            border=ft.Border(right=ft.BorderSide(1, "#252d3f")),
        ),
        ft.Container(content=detail_col, expand=True, padding=20),
    ], expand=True)



