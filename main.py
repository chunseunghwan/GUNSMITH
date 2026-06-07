# -*- coding: utf-8 -*-
"""
GUNSMITH — PUBG 총기 커스텀 & 반동 분석 시스템
Flet + DuckDB
학번: 20231161  성명: 천승환
"""
import os
import sys

# 프로젝트 루트를 sys.path에 추가 (모듈 임포트 경로 보장)
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import flet as ft

from db_init import init_db
from database import Database

from repository.duckdb.weapon_repository import WeaponRepository, WeaponRecoilRepository
from repository.duckdb.attachment_repository import AttachmentRepository, WeaponAttachmentCompatRepository
from repository.duckdb.custom_repository import CustomConfigRepository, RecoilResultRepository, WeaponQueryRepository

from service.weapon_service import WeaponService
from service.attachment_service import AttachmentService
from service.custom_service import CustomService
from service.compare_service import CompareService

from view.weapon_view import build_weapon_view
from view.attachment_view import build_attachment_view
from view.custom_view import build_custom_view
from view.compare_view import build_compare_view

BG     = "#0d1117"
ACCENT = "#4fc3f7"
DIM    = "#6b7585"


def main(page: ft.Page):
    # ── DB 초기화 ─────────────────────────────────────────────────
    init_db()
    db = Database()

    # ── 레포지토리 ────────────────────────────────────────────────
    weapon_repo       = WeaponRepository(db)
    weapon_recoil_repo = WeaponRecoilRepository(db)
    attachment_repo   = AttachmentRepository(db)
    compat_repo       = WeaponAttachmentCompatRepository(db)
    config_repo       = CustomConfigRepository(db)
    result_repo       = RecoilResultRepository(db)
    query_repo        = WeaponQueryRepository(db)

    # ── 서비스 ────────────────────────────────────────────────────
    weapon_service     = WeaponService(weapon_repo, weapon_recoil_repo, query_repo)
    attachment_service = AttachmentService(attachment_repo, compat_repo)
    custom_service     = CustomService(config_repo, result_repo, query_repo, compat_repo, db)
    compare_service    = CompareService(query_repo, config_repo, result_repo)

    # ── 페이지 설정 ───────────────────────────────────────────────
    page.title      = "GUNSMITH — PUBG 총기 커스텀 시스템"
    page.bgcolor    = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.theme      = ft.Theme(color_scheme_seed=ACCENT)
    page.window.width      = 1260
    page.window.height     = 820
    page.window.min_width  = 900
    page.window.min_height = 600
    page.padding = 0

    # ── 뷰 빌드 ──────────────────────────────────────────────────
    weapon_view     = build_weapon_view(page, weapon_service)
    attachment_view = build_attachment_view(page, attachment_service)
    custom_view     = build_custom_view(page, custom_service, weapon_service)
    compare_view    = build_compare_view(page, compare_service)

    # ── 탭 (ft.Tabs 대신 커스텀 버튼 Row — Flet 버전 무관하게 안정적) ──
    TAB_LABELS = ["🔫  총기 정보", "🔧  파츠 정보", "⚙️  파츠 커스텀", "📊  비교 분석"]
    views      = [weapon_view, attachment_view, custom_view, compare_view]
    view_pad   = [0, 0, 16, 16]

    content_containers = [
        ft.Container(content=v, expand=True, padding=view_pad[i], visible=(i == 0))
        for i, v in enumerate(views)
    ]
    content_stack = ft.Stack(content_containers, expand=True)

    tab_btns: list[ft.Container] = []
    cur_tab  = [0]   # mutable index

    def _select_tab(idx: int):
        cur_tab[0] = idx
        for i, (btn, box) in enumerate(zip(tab_btns, content_containers)):
            active = (i == idx)
            box.visible = active
            btn.bgcolor = ACCENT if active else "#161b27"
            btn.border  = ft.Border.all(1, ACCENT) if active else ft.Border.all(1, "#2a3040")
            txt = btn.content
            txt.color   = "#0d1117" if active else DIM
        content_stack.update()
        for b in tab_btns:
            b.update()

    def _make_tab_btn(label: str, idx: int) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=13, weight=ft.FontWeight.W_600,
                            color=ACCENT if idx == 0 else DIM),
            bgcolor=ACCENT if idx == 0 else "#161b27",
            border=ft.Border.all(1, ACCENT) if idx == 0 else ft.Border.all(1, "#2a3040"),
            border_radius=6,
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            on_click=lambda e, i=idx: _select_tab(i),
            ink=True,
        )

    for i, lbl in enumerate(TAB_LABELS):
        tab_btns.append(_make_tab_btn(lbl, i))

    tab_bar = ft.Container(
        content=ft.Row(tab_btns, spacing=6),
        bgcolor="#0a0e18",
        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
        border=ft.Border(bottom=ft.BorderSide(1, "#1e2535")),
    )

    # ── 헤더 ─────────────────────────────────────────────────────
    header = ft.Container(
        content=ft.Row([
            ft.Text("GUNSMITH", color=ACCENT, size=20, weight=ft.FontWeight.BOLD,
                    font_family="monospace"),
            ft.Text("|  PUBG 총기 커스텀 & 반동 분석 시스템", color=DIM, size=13),
            ft.Container(expand=True),
            ft.Text("DuckDB  ·  Flet", color="#2a3a50", size=11),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        bgcolor="#090d14",
        padding=ft.Padding(left=20, right=20, top=12, bottom=12),
        border=ft.Border(bottom=ft.BorderSide(1, "#1e2535")),
    )

    page.add(ft.Column([header, tab_bar, content_stack], expand=True, spacing=0))


ft.run(main, assets_dir=ROOT)   # ROOT 기준 상대경로로 img/weapon/*.webp 로드
