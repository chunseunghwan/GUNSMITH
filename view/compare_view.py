import flet as ft

CARD2  = "#1e2535"
ACCENT = "#4fc3f7"
TEXT   = "#dde3ed"
DIM    = "#6b7585"
GREEN  = "#66BB6A"
RED    = "#ff5252"
GOLD   = "#FFD700"

GRADE_COLOR = {'S': GOLD, 'A': ACCENT, 'B': GREEN, 'C': '#FF7043'}

RECOIL_FIELDS = [
    ('final_recoil_vertical',   '수직 반동',    12.0),
    ('final_recoil_horizontal', '좌우 반동',     6.0),
    ('final_muzzle_rise',       '총구 들림',    12.0),
    ('final_muzzle_shake',      '총구 흔들림',   6.0),
    ('final_first_shot_recoil', '초탄 반동',    15.0),
    ('final_recoil_recovery',   '반동 회복',     6.0),
]


def build_compare_view(page: ft.Page, compare_service) -> ft.Control:
    compare_col = ft.Column(
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=8,
        controls=[ft.Text("저장된 커스텀 두 개를 선택해 비교하세요.", color=DIM, size=13)],
    )

    def load_dropdowns():
        df = compare_service.get_all_configs()
        opts = [ft.dropdown.Option('없음', '선택하세요')]
        for _, r in df.iterrows():
            opts.append(ft.dropdown.Option(
                str(int(r['config_id'])),
                f"[{r['config_id']}] {r['custom_name']}  ({r['weapon_name']})"
            ))
        left_dd.options = opts
        right_dd.options = [o for o in opts]
        try:
            left_dd.update()
            right_dd.update()
        except Exception:
            pass

    def on_compare(e):
        lv = left_dd.value
        rv = right_dd.value
        if not lv or not rv or lv == '없음' or rv == '없음':
            compare_col.controls = [ft.Text("⚠  두 개의 커스텀을 모두 선택하세요.", color=RED, size=13)]
            compare_col.update()
            return
        if lv == rv:
            compare_col.controls = [ft.Text("⚠  서로 다른 커스텀을 선택하세요.", color=RED, size=13)]
            compare_col.update()
            return

        df = compare_service.get_compare_data(int(lv), int(rv))
        if df.empty or len(df) < 2:
            compare_col.controls = [ft.Text("반동 결과 데이터가 없습니다. 커스텀 저장 시 계산 결과도 함께 저장됩니다.", color=RED, size=12)]
            compare_col.update()
            return

        L = df[df['config_id'] == int(lv)].iloc[0].to_dict()
        R = df[df['config_id'] == int(rv)].iloc[0].to_dict()

        def side_header(d):
            grade = str(d.get('stability_grade') or '?')
            gc = GRADE_COLOR.get(grade, DIM)
            score = int(d.get('stability_score') or 0)
            return ft.Column([
                ft.Text(d.get('custom_name',''), color=TEXT, size=15,
                        weight=ft.FontWeight.BOLD),
                ft.Text(d.get('weapon_name',''), color=ACCENT, size=12),
                ft.Row([
                    ft.Container(
                        content=ft.Text(grade, color="#0d1117", size=13,
                                        weight=ft.FontWeight.BOLD),
                        bgcolor=gc, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                        border_radius=8,
                    ),
                    ft.Text(f"{score} / 100", color=gc, size=14,
                            weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.ProgressBar(value=score/100, bgcolor="#252d3f", color=gc,
                               height=10, border_radius=5),
            ], spacing=6, expand=True)

        def build_row(field, label, max_val):
            lv_ = float(L.get(field) or 0)
            rv_ = float(R.get(field) or 0)
            # 낮을수록 좋음 (반동 회복 제외)
            is_recovery = (field == 'final_recoil_recovery')
            if is_recovery:
                l_better = lv_ >= rv_
            else:
                l_better = lv_ <= rv_

            lc = GREEN if l_better else RED
            rc = GREEN if not l_better else RED
            if abs(lv_ - rv_) < 0.001:
                lc = rc = ACCENT

            lp = min(lv_ / max_val, 1.0)
            rp = min(rv_ / max_val, 1.0)

            return ft.Container(
                content=ft.Column([
                    ft.Text(label, color=DIM, size=11,
                            text_align=ft.TextAlign.CENTER),
                    ft.Row([
                        # 좌측 바 (우에서 좌로)
                        ft.Column([
                            ft.Row([
                                ft.Text(f"{lv_:.4f}", color=lc, size=12,
                                        weight=ft.FontWeight.W_600),
                                ft.ProgressBar(value=lp, bgcolor="#252d3f", color=lc,
                                               height=8, border_radius=4, expand=True),
                            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ], expand=True),
                        ft.Container(width=16),
                        # 우측 바
                        ft.Column([
                            ft.Row([
                                ft.ProgressBar(value=rp, bgcolor="#252d3f", color=rc,
                                               height=8, border_radius=4, expand=True),
                                ft.Text(f"{rv_:.4f}", color=rc, size=12,
                                        weight=ft.FontWeight.W_600),
                            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ], expand=True),
                    ], spacing=0),
                ], spacing=4),
                bgcolor=CARD2, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                border_radius=8,
            )

        compare_col.controls = [
            # 헤더 ────────────────────────────────────────
            ft.Container(
                content=ft.Row([
                    side_header(L),
                    ft.VerticalDivider(width=1, color="#252d3f"),
                    side_header(R),
                ], spacing=16),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),
            ft.Row([
                ft.Container(
                    content=ft.Text("← 파란색·초록색 = 더 우수", color=GREEN, size=11),
                    expand=True, padding=ft.Padding(left=6, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text("빨간색 = 더 높은 반동 (불리) →", color=RED, size=11),
                    expand=True, padding=ft.Padding(left=0, right=6, top=0, bottom=0),
                    alignment=ft.Alignment.CENTER_RIGHT,
                ),
            ]),
            # 반동 비교 행 ─────────────────────────────────
            *[build_row(f, lbl, mx) for f, lbl, mx in RECOIL_FIELDS],
            ft.Text("※ 비교 결과는 임시 표시이며 저장되지 않습니다.", color=DIM, size=10),
        ]
        compare_col.update()

    def on_refresh(e):
        load_dropdowns()

    left_dd = ft.Dropdown(
        value='없음', options=[ft.dropdown.Option('없음','선택하세요')],
        bgcolor=CARD2, color=TEXT, border_color=ACCENT, width=320, text_size=12,
    )
    right_dd = ft.Dropdown(
        value='없음', options=[ft.dropdown.Option('없음','선택하세요')],
        bgcolor=CARD2, color=TEXT, border_color=ACCENT, width=320, text_size=12,
    )

    compare_btn = ft.ElevatedButton(
        content=ft.Text("비교하기"),
        icon=ft.Icons.COMPARE_ARROWS,
        style=ft.ButtonStyle(
            bgcolor=ACCENT, color="#0d1117",
            padding=ft.Padding(left=0, right=0, top=0, bottom=0),
        ),
        on_click=on_compare,
    )
    refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH, icon_color=ACCENT,
        tooltip="커스텀 목록 새로고침",
        on_click=on_refresh,
    )

    load_dropdowns()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("좌측 커스텀", color=DIM, size=11),
                    left_dd,
                ], spacing=4),
                ft.Column([
                    ft.Text("우측 커스텀", color=DIM, size=11),
                    right_dd,
                ], spacing=4),
                ft.Column([
                    ft.Text(" ", size=11),
                    ft.Row([compare_btn, refresh_btn], spacing=6),
                ], spacing=4),
            ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.END),
            bgcolor=CARD2, padding=16, border_radius=10,
        ),
        compare_col,
    ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True)


