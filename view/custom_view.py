import flet as ft

CARD2  = "#1e2535"
ACCENT = "#4fc3f7"
TEXT   = "#dde3ed"
DIM    = "#6b7585"
GREEN  = "#66BB6A"
RED    = "#ff5252"
GOLD   = "#FFD700"

SLOTS = ['muzzle', 'stock', 'grip', 'magazine', 'scope', 'foregrip']
SLOT_KR = {
    'muzzle':   '총구',
    'stock':    '개머리판',
    'grip':     '손잡이',
    'magazine': '탄창',
    'scope':    '조준경',
    'foregrip': '전술손잡이',
}
SLOT_TYPE = {
    'muzzle': 'Muzzle', 'stock': 'Stock', 'grip': 'Grip',
    'magazine': 'Magazine', 'scope': 'Scope', 'foregrip': 'Foregrip',
}
GRADE_COLOR = {'S': GOLD, 'A': ACCENT, 'B': GREEN, 'C': '#FF7043'}


def build_custom_view(page: ft.Page, custom_service, weapon_service) -> ft.Control:
    # ── 상태 ─────────────────────────────────────────────────────
    state = {
        'weapon_id': None,
        'base_recoil': {},
        'slots': {s: None for s in SLOTS},
        'result': {},
    }

    # ── 위젯 참조 ─────────────────────────────────────────────────
    slot_dropdowns: dict[str, ft.Dropdown] = {}
    name_field = ft.TextField(
        label="커스텀 이름", hint_text="저장할 이름을 입력하세요",
        bgcolor=CARD2, color=TEXT, border_color=ACCENT,
        label_style=ft.TextStyle(color=DIM), cursor_color=ACCENT,
        width=300, text_size=13,
    )
    result_col  = ft.Column(spacing=6)
    save_status = ft.Text("", color=GREEN, size=13)

    # ── 반동 결과 갱신 ────────────────────────────────────────────
    def refresh_result():
        wid = state['weapon_id']
        if wid is None:
            return
        r = custom_service.calculate_recoil(wid, state['slots'])
        state['result'] = r
        b = state['base_recoil']

        score = r.get('stability_score', 0)
        grade = r.get('stability_grade', '?')
        b_score = b.get('stability_score', 0)
        gc = GRADE_COLOR.get(grade, DIM)

        def diff_row(label, base_key, final_key):
            bv = float(b.get(base_key) or 0)
            fv = float(r.get(final_key) or 0)
            diff = fv - bv
            if diff < -0.001:
                diff_text = f"  ▼ {abs(diff):.2f}"
                dc = GREEN
            elif diff > 0.001:
                diff_text = f"  ▲ {abs(diff):.2f}"
                dc = RED
            else:
                diff_text = "  —"
                dc = DIM
            return ft.Row([
                ft.Text(label, color=DIM, size=12, width=110),
                ft.Text(f"{bv:.2f}", color=DIM, size=12, width=55),
                ft.Text("→", color=DIM, size=11, width=18),
                ft.Text(f"{fv:.2f}", color=TEXT, size=12, weight=ft.FontWeight.W_600, width=55),
                ft.Text(diff_text, color=dc, size=11),
            ])

        result_col.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text("■  안정성 변화", color=ACCENT, size=13, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Text("기본:", color=DIM, size=12, width=45),
                        ft.ProgressBar(
                            value=b_score/100, bgcolor="#252d3f", color="#aaa",
                            height=10, border_radius=5, expand=True,
                        ),
                        ft.Text(f"{b_score}", color=DIM, size=12, width=32,
                                text_align=ft.TextAlign.RIGHT),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    ft.Row([
                        ft.Text("파츠:", color=ACCENT, size=12, width=45),
                        ft.ProgressBar(
                            value=score/100, bgcolor="#252d3f", color=ACCENT,
                            height=10, border_radius=5, expand=True,
                        ),
                        ft.Text(f"{score}", color=ACCENT, size=12, width=32,
                                text_align=ft.TextAlign.RIGHT),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    ft.Row([
                        ft.Text(f"최종 등급:", color=DIM, size=12),
                        ft.Container(
                            content=ft.Text(grade, color="#0d1117", size=14,
                                            weight=ft.FontWeight.BOLD),
                            bgcolor=gc, padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                            border_radius=10,
                        ),
                    ], spacing=8),
                ], spacing=8),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("■  반동 수치 변화  (기본 → 파츠 적용)",
                            color=ACCENT, size=13, weight=ft.FontWeight.BOLD),
                    diff_row("수직 반동",   'recoil_vertical',   'final_recoil_vertical'),
                    diff_row("좌우 반동",   'recoil_horizontal', 'final_recoil_horizontal'),
                    diff_row("총구 들림",   'muzzle_rise',       'final_muzzle_rise'),
                    diff_row("총구 흔들림", 'muzzle_shake',      'final_muzzle_shake'),
                    diff_row("초탄 반동",   'first_recoil',      'final_first_shot_recoil'),
                    diff_row("반동 회복",   'recovery_recoil',   'final_recoil_recovery'),
                ], spacing=6),
                bgcolor=CARD2, padding=14, border_radius=10,
            ),
        ]
        result_col.update()

    # ── 슬롯 드롭다운 갱신 ────────────────────────────────────────
    def rebuild_slot_dropdowns(weapon_id: int):
        for slot_key in SLOTS:
            slot_type = SLOT_TYPE[slot_key]
            compat_df = custom_service.get_compat_by_slot(weapon_id, slot_type)

            opts = [ft.dropdown.Option('없음', '장착 안 함')]
            for _, r in compat_df.iterrows():
                opts.append(ft.dropdown.Option(
                    str(int(r['attachment_id'])), r['attachment_name']
                ))

            dd = slot_dropdowns[slot_key]
            dd.options = opts
            dd.value = '없음'
            dd.disabled = len(opts) <= 1
            state['slots'][slot_key] = None

        for dd in slot_dropdowns.values():
            dd.update()
        refresh_result()

    def on_slot_change(e, slot_key: str):
        val = e.control.value
        state['slots'][slot_key] = int(val) if val and val != '없음' else None
        refresh_result()

    # ── 무기 선택 ─────────────────────────────────────────────────
    def on_weapon_change(e):
        val = e.control.value
        if not val or val == '선택':
            return
        wid = int(val)
        state['weapon_id'] = wid
        data = weapon_service.get_with_recoil(wid)
        state['base_recoil'] = data.get('recoil', {})
        rebuild_slot_dropdowns(wid)

    # 무기 드롭다운 초기화
    all_weapons = weapon_service.get_all()
    weapon_opts = [ft.dropdown.Option('선택', '총기를 선택하세요')]
    for _, r in all_weapons.iterrows():
        weapon_opts.append(ft.dropdown.Option(
            str(int(r['weapon_id'])),
            f"{r['weapon_name']}  [{r['gun_type']}]"
        ))

    weapon_dd = ft.Dropdown(
        value='선택',
        options=weapon_opts,
        on_select=on_weapon_change,
        bgcolor=CARD2, color=TEXT, border_color=ACCENT, width=280, text_size=13,
    )

    # 슬롯 드롭다운 생성
    for sk in SLOTS:
        slot_dropdowns[sk] = ft.Dropdown(
            value='없음',
            options=[ft.dropdown.Option('없음', '장착 안 함')],
            on_select=lambda e, s=sk: on_slot_change(e, s),
            bgcolor=CARD2, color=TEXT, border_color="#3a4558", width=240,
            text_size=12, disabled=True,
        )

    def on_save(e):
        wid = state['weapon_id']
        cname = name_field.value.strip()
        if wid is None:
            save_status.value = "⚠ 총기를 먼저 선택하세요."
            save_status.color = RED
            save_status.update()
            return
        if not cname:
            save_status.value = "⚠ 커스텀 이름을 입력하세요."
            save_status.color = RED
            save_status.update()
            return

        try:
            config_id = custom_service.save_custom(wid, cname, state['slots'].copy())
            save_status.value = f"✓ 저장 완료  (ID: {config_id})"
            save_status.color = GREEN
            name_field.value = ""
            name_field.update()
        except Exception as ex:
            save_status.value = f"저장 실패: {ex}"
            save_status.color = RED
        save_status.update()

    save_btn = ft.ElevatedButton(
        content=ft.Text("커스텀 저장"),
        icon=ft.Icons.SAVE_ALT,
        style=ft.ButtonStyle(
            bgcolor=ACCENT, color="#0d1117",
            padding=ft.Padding(left=0, right=0, top=0, bottom=0),
        ),
        on_click=on_save,
    )

    # ── 슬롯 패널 ─────────────────────────────────────────────────
    slot_rows = []
    for sk in SLOTS:
        slot_rows.append(ft.Row([
            ft.Text(SLOT_KR[sk], color=TEXT, size=13, width=80),
            slot_dropdowns[sk],
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12))

    left_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("총기 선택:", color=TEXT, size=13),
                weapon_dd,
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(color="#252d3f"),
            ft.Text("■  슬롯 파츠 선택", color=ACCENT, size=13, weight=ft.FontWeight.BOLD),
            *slot_rows,
            ft.Divider(color="#252d3f"),
            name_field,
            ft.Row([save_btn, save_status], spacing=12,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=12, scroll=ft.ScrollMode.AUTO),
        width=420,
        padding=ft.Padding(left=14, right=14, top=16, bottom=16),
        border=ft.Border(right=ft.BorderSide(1, "#252d3f")),
    )

    right_panel = ft.Container(
        content=ft.Column([
            ft.Text("■  반동 계산 결과", color=ACCENT, size=14, weight=ft.FontWeight.BOLD),
            ft.Text("파츠를 선택하면 실시간으로 반동 수치가 변동됩니다.", color=DIM, size=11),
            result_col,
        ], spacing=10, scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=20,
    )

    return ft.Row([left_panel, right_panel], expand=True)



