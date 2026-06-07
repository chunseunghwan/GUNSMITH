# -*- coding: utf-8 -*-
"""
DuckDB 스키마 생성 및 초기 데이터 삽입 (v2 - 실제 PUBG 데이터 기반)
---------------------------------------------------------------------------
fire_speed 단위 : 초/발 (seconds per shot)  ex) M416 0.0857 ≈ 700 RPM
안정성 공식     : per_shot = min((vert+horiz+rise+shake)/2, 4.0)
                  fire_recoil = per_shot * 1.2 / fire_speed
                  score = max(0, min(100, round(100 - fire_recoil)))
"""
import os
import duckdb

DB_PATH  = os.path.join(os.path.dirname(__file__), "GUNSMITH_DB.duckdb")
_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "weapon")


# ═══════════════════════════════════════════════════════════════
# DDL
# ═══════════════════════════════════════════════════════════════
def _create_tables(conn: duckdb.DuckDBPyConnection):
    conn.execute("DROP TABLE IF EXISTS RECOIL_RESULT")
    conn.execute("DROP TABLE IF EXISTS CUSTOM_CONFIG")
    conn.execute("DROP TABLE IF EXISTS WEAPON_ATTACHMENT_COMPAT")
    conn.execute("DROP TABLE IF EXISTS ATTACHMENT")
    conn.execute("DROP TABLE IF EXISTS WEAPON_RECOIL")
    conn.execute("DROP TABLE IF EXISTS WEAPON")

    # ── WEAPON ────────────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE WEAPON (
            weapon_id    INTEGER PRIMARY KEY,
            weapon_name  VARCHAR(50) NOT NULL UNIQUE,
            gun_type     VARCHAR(10),
            bullet_type  VARCHAR(15),
            damage       FLOAT,
            bullet_speed FLOAT,
            fire_speed   FLOAT,          -- 초/발 (seconds per shot)
            description  TEXT,
            is_custom    BOOLEAN,
            image_path   VARCHAR(255)
        )
    """)

    # ── WEAPON_RECOIL ─────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE WEAPON_RECOIL (
            recoil_id         INTEGER PRIMARY KEY,
            weapon_id         INTEGER NOT NULL UNIQUE,
            recoil_vertical   FLOAT,
            recoil_horizontal FLOAT,
            pattern_scale     FLOAT,
            first_recoil      FLOAT,
            crouch_modifier   FLOAT,
            prone_modifier    FLOAT,
            muzzle_rise       FLOAT,
            muzzle_shake      FLOAT,
            recovery_recoil   FLOAT,
            vertical_speed    FLOAT,
            stability_score   INTEGER,
            stability_grade   VARCHAR(1),
            FOREIGN KEY (weapon_id) REFERENCES WEAPON(weapon_id)
        )
    """)

    # ── ATTACHMENT (파츠 기본 보정값 포함) ────────────────────────
    conn.execute("""
        CREATE TABLE ATTACHMENT (
            attachment_id             INTEGER PRIMARY KEY,
            attachment_name           VARCHAR(60) NOT NULL,
            slot_type                 VARCHAR(15),
            image_path                VARCHAR(255),
            control_recoil_vertical   FLOAT DEFAULT 0.0,
            control_recoil_horizontal FLOAT DEFAULT 0.0,
            control_muzzle_rise       FLOAT DEFAULT 0.0,
            control_muzzle_shake      FLOAT DEFAULT 0.0,
            mod_recovery_recoil       FLOAT DEFAULT 0.0,
            control_first_recoil      FLOAT DEFAULT 0.0
        )
    """)

    # ── WEAPON_ATTACHMENT_COMPAT (총기별 보정값) ──────────────────
    conn.execute("""
        CREATE TABLE WEAPON_ATTACHMENT_COMPAT (
            compat_id                 INTEGER PRIMARY KEY,
            weapon_id                 INTEGER NOT NULL,
            attachment_id             INTEGER NOT NULL,
            control_recoil_vertical   FLOAT DEFAULT 0.0,
            control_recoil_horizontal FLOAT DEFAULT 0.0,
            control_muzzle_rise       FLOAT DEFAULT 0.0,
            control_muzzle_shake      FLOAT DEFAULT 0.0,
            mod_recovery_recoil       FLOAT DEFAULT 0.0,
            control_first_recoil      FLOAT DEFAULT 0.0,
            FOREIGN KEY (weapon_id)     REFERENCES WEAPON(weapon_id),
            FOREIGN KEY (attachment_id) REFERENCES ATTACHMENT(attachment_id)
        )
    """)

    # ── CUSTOM_CONFIG ─────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE CUSTOM_CONFIG (
            config_id   INTEGER PRIMARY KEY,
            weapon_id   INTEGER NOT NULL,
            custom_name VARCHAR(50),
            muzzle_id   INTEGER,
            stock_id    INTEGER,
            grip_id     INTEGER,
            magazine_id INTEGER,
            scope_id    INTEGER,
            foregrip_id INTEGER,
            created_at  TIMESTAMP,
            FOREIGN KEY (weapon_id)   REFERENCES WEAPON(weapon_id),
            FOREIGN KEY (muzzle_id)   REFERENCES ATTACHMENT(attachment_id),
            FOREIGN KEY (stock_id)    REFERENCES ATTACHMENT(attachment_id),
            FOREIGN KEY (grip_id)     REFERENCES ATTACHMENT(attachment_id),
            FOREIGN KEY (magazine_id) REFERENCES ATTACHMENT(attachment_id),
            FOREIGN KEY (scope_id)    REFERENCES ATTACHMENT(attachment_id),
            FOREIGN KEY (foregrip_id) REFERENCES ATTACHMENT(attachment_id)
        )
    """)

    # ── RECOIL_RESULT ─────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE RECOIL_RESULT (
            result_id               INTEGER PRIMARY KEY,
            config_id               INTEGER NOT NULL UNIQUE,
            final_recoil_vertical   FLOAT,
            final_recoil_horizontal FLOAT,
            final_muzzle_rise       FLOAT,
            final_muzzle_shake      FLOAT,
            final_first_shot_recoil FLOAT,
            final_recoil_recovery   FLOAT,
            stability_score         INTEGER,
            stability_grade         VARCHAR(1),
            FOREIGN KEY (config_id) REFERENCES CUSTOM_CONFIG(config_id)
        )
    """)


# ═══════════════════════════════════════════════════════════════
# 안정성 계산 공식
# ═══════════════════════════════════════════════════════════════
def _calc_stability(vert, horiz, rise, shake, fire_speed, gun_type):
    """
    설계서 10절 공식 (fire_speed 단위: 초/발)
      per_shot    = min((vert+horiz+rise+shake)/2, 4.0)
      fire_recoil = per_shot * 1.2 / fire_speed   (≡ per_shot * RPM/50)
      score       = max(0, min(100, round(100-fire_recoil)))
    샷건은 제외 → 0/C
    """
    if gun_type == 'SG':
        return 0, 'C'
    per_shot    = min((vert + horiz + rise + shake) / 2, 4.0)
    fire_recoil = per_shot * 1.2 / fire_speed
    score = max(0, min(100, round(100 - fire_recoil)))
    grade = 'S' if score >= 80 else 'A' if score >= 60 else 'B' if score >= 40 else 'C'
    return score, grade


# ═══════════════════════════════════════════════════════════════
# 반동 템플릿 (총기 타입 × 탄약 타입)
# (vert, horiz, pattern, first, crouch, prone, rise, shake, recovery, vert_spd)
# ═══════════════════════════════════════════════════════════════
_TPL = {
    'AR_556':  (2.3, 0.9, 0.80, 3.2, 0.85, 0.70, 1.1, 0.8, 1.9, 2.1),
    'AR_762':  (3.2, 1.4, 1.10, 4.5, 0.85, 0.70, 1.9, 1.1, 1.5, 2.7),
    'SMG_9mm': (1.9, 1.1, 0.65, 2.6, 0.85, 0.70, 0.9, 0.7, 2.2, 1.9),
    'SMG_45':  (2.2, 1.3, 0.75, 3.0, 0.85, 0.70, 1.1, 0.8, 2.0, 2.1),
    'SMG_57':  (1.7, 1.0, 0.60, 2.3, 0.85, 0.70, 0.8, 0.6, 2.3, 1.8),
    'DMR_556': (2.8, 1.3, 1.00, 4.2, 0.85, 0.70, 1.5, 1.1, 1.6, 2.5),
    'DMR_762': (4.2, 1.9, 1.40, 5.8, 0.85, 0.70, 2.3, 1.5, 1.1, 3.3),
    'DMR_9mm': (2.5, 1.2, 0.90, 3.8, 0.85, 0.70, 1.3, 1.0, 1.8, 2.3),
    'LMG':     (3.3, 1.7, 1.20, 4.8, 0.85, 0.70, 1.9, 1.5, 1.3, 2.7),
    'SR':      (8.0, 1.5, 2.00,10.0, 0.85, 0.70, 5.0, 2.0, 0.5, 6.0),
    'SG':      (10.0,3.0, 3.00,15.0, 0.85, 0.70, 8.0, 3.0, 0.3, 8.0),
    'Pistol':  (3.3, 2.0, 1.20, 4.2, 0.85, 0.70, 1.9, 1.4, 1.8, 2.8),
}

def _get_template(gun_type: str, bullet_type: str) -> tuple:
    if gun_type == 'AR':
        return _TPL['AR_762'] if '7.62' in bullet_type else _TPL['AR_556']
    if gun_type == 'SMG':
        if '.45' in bullet_type: return _TPL['SMG_45']
        if '5.7' in bullet_type: return _TPL['SMG_57']
        return _TPL['SMG_9mm']
    if gun_type == 'DMR':
        if '9mm' in bullet_type: return _TPL['DMR_9mm']
        return _TPL['DMR_762'] if '7.62' in bullet_type else _TPL['DMR_556']
    return _TPL.get(gun_type, _TPL['Pistol'])


# ═══════════════════════════════════════════════════════════════
# 데이터 삽입
# ═══════════════════════════════════════════════════════════════
def _insert_weapons(conn):
    # (id, name, type, bullet, dmg, bullet_speed, fire_speed[초/발], desc, is_custom, image_path)
    # image_path: 로컬 파일 우선, 없으면 placehold.co URL 폴백
    _C = {
        'AR': '4fc3f7', 'SMG': '66bb6a', 'DMR': 'ffd700',
        'LMG': 'ab47bc', 'SR': 'ff9800', 'SG': 'f44336', 'Pistol': '9e9e9e',
    }
    # 예외 매핑 (DB명과 파일명이 다른 경우만), 기본: 공백 -> _
    _EX = {'QBZ95': 'QBZ', 'Mini 14': 'Mini14', 'Mk14 EBR': 'MK14'}
    def url(name, t):
        fname = _EX.get(name, name.replace(' ', '_'))
        local = os.path.join(_IMG_DIR, fname + '.webp')
        if os.path.exists(local):
            return f'img/weapon/{fname}.webp'    # assets_dir 기준 상대 경로
        # 이미지 없는 총기(MP9, JS9 등) → URL 플레이스홀더
        c = _C.get(t, 'aaaaaa')
        n = name.replace(' ', '+')
        return f'https://placehold.co/180x100/0d1117/{c}?text={n}'

    weapons = [
        # ── AR ──────────────────────────────────────────────────
        (1,  'M416',        'AR',     '5.56mm',   40.0,  880.0, 0.0857,
         'PUBG의 대표 AR. 안정적인 반동과 다양한 파츠 호환성을 자랑한다.',         True,  url('M416','AR')),
        (2,  'AKM',         'AR',     '7.62mm',   48.0,  715.0, 0.100,
         '높은 데미지와 강한 반동의 AR. 7.62mm 탄 사용으로 방어구 관통에 유리.',   True,  url('AKM','AR')),
        (3,  'SCAR-L',      'AR',     '5.56mm',   42.0,  870.0, 0.092,
         '낮은 반동과 안정적인 연사가 특징인 AR.',                                  True,  url('SCAR-L','AR')),
        (4,  'M16A4',       'AR',     '5.56mm',   43.0,  910.0, 0.075,
         '3점사·단발 모드만 지원하는 AR. 정확성이 뛰어나다.',                       True,  url('M16A4','AR')),
        (5,  'Groza',       'AR',     '7.62mm',   47.0,  715.0, 0.080,
         '드랍 전용 AR. 내장 소음기와 강력한 화력을 보유.',                         True,  url('Groza','AR')),
        (6,  'AUG A3',      'AR',     '5.56mm',   40.0,  890.0, 0.083,
         '에어드롭 전용 AR. 장탄 수와 안정성이 우수하다.',                           True,  url('AUG A3','AR')),
        (7,  'Beryl M762',  'AR',     '7.62mm',   44.0,  740.0, 0.086,
         '7.62mm AR 중 연사속도가 빠른 편. 반동 제어가 관건.',                      True,  url('Beryl M762','AR')),
        (8,  'QBZ95',       'AR',     '5.56mm',   42.0,  930.0, 0.0923,
         '중국 맵 전용 AR. QBZ 전용 파츠를 사용한다.',                              True,  url('QBZ95','AR')),
        (9,  'G36C',        'AR',     '5.56mm',   41.0,  870.0, 0.0857,
         '전술적 사격에 최적화된 AR.',                                               True,  url('G36C','AR')),
        (10, 'MK47 Mutant', 'AR',     '7.62mm',   49.0,  780.0, 0.075,
         '2점사 모드를 지원하는 7.62mm AR. 중거리 정밀 사격에 강함.',                True,  url('MK47 Mutant','AR')),
        (11, 'ACE32',       'AR',     '7.62mm',   43.0,  720.0, 0.088,
         '7.62mm 탄약을 사용하는 AR. 비교적 안정적인 반동.',                         True,  url('ACE32','AR')),
        (12, 'FAMAS',       'AR',     '5.56mm',   39.0,  925.0, 0.067,
         '3점사 특화 AR. 버스트 사격 시 높은 명중률을 보인다.',                       True,  url('FAMAS','AR')),
        (13, 'K2',          'AR',     '5.56mm',   41.0,  880.0, 0.0857,
         '한국 맵 전용 AR. M416과 유사한 성능.',                                     True,  url('K2','AR')),
        # ── SMG ─────────────────────────────────────────────────
        (14, 'UMP45',       'SMG',    '.45 ACP',  42.0,  360.0, 0.089,
         '높은 데미지의 .45 ACP 탄을 사용하는 SMG.',                                 True,  url('UMP45','SMG')),
        (15, 'Vector',      'SMG',    '9mm',      32.55, 345.0, 0.055,
         '초당 발사속도가 매우 빠른 SMG. 탄창 소모가 빨라 확장 탄창이 필수.',         True,  url('Vector','SMG')),
        (16, 'UZI',         'SMG',    '9mm',      27.3,  350.0, 0.048,
         '게임 최고 연사속도 SMG. 근거리 DPS 최강.',                                  True,  url('UZI','SMG')),
        (17, 'Tommy Gun',   'SMG',    '9mm',      40.0,  280.0, 0.080,
         '대용량 드럼 탄창의 SMG. 안정적이고 높은 데미지.',                           True,  url('Tommy Gun','SMG')),
        (18, 'MP5K',        'SMG',    '9mm',      33.6,  380.0, 0.067,
         '균형 잡힌 성능의 SMG. 다양한 파츠 장착 가능.',                             True,  url('MP5K','SMG')),
        (19, 'MP9',         'SMG',    '9mm',      32.55, 400.0, 0.060,
         '빠른 연사와 작은 크기의 SMG.',                                              True,  url('MP9','SMG')),
        (20, 'JS9',         'SMG',    '9mm',      33.6,  360.0, 0.067,
         '중국 맵 전용 SMG.',                                                         True,  url('JS9','SMG')),
        (21, 'P90',         'SMG',    '5.7mm',    36.75, 715.0, 0.060,
         '50발 대용량 탄창의 SMG. 낮은 반동과 준수한 데미지.',                        True,  url('P90','SMG')),
        # ── DMR ─────────────────────────────────────────────────
        (22, 'SKS',         'DMR',    '7.62mm',   49.35, 800.0, 0.163,
         '높은 데미지의 반자동 DMR. 파츠 장착으로 반동 제어가 가능하다.',             True,  url('SKS','DMR')),
        (23, 'Mini 14',     'DMR',    '5.56mm',   44.1,  990.0, 0.180,
         '높은 탄속과 낮은 반동의 DMR. 원거리 빠른 조준 사격에 유리.',               True,  url('Mini 14','DMR')),
        (24, 'VSS',         'DMR',    '9mm',      47.25, 430.0, 0.0856,
         '드랍 전용 DMR. 내장 소음기와 스코프를 장착한 암살 특화 총기.',              True,  url('VSS','DMR')),
        (25, 'QBU',         'DMR',    '5.56mm',   44.1,  990.0, 0.180,
         '중국 맵 전용 DMR. Mini 14와 유사한 성능.',                                  True,  url('QBU','DMR')),
        (26, 'MK12',        'DMR',    '5.56mm',   46.2,  900.0, 0.180,
         '5.56mm DMR 중 높은 데미지를 보유.',                                         True,  url('MK12','DMR')),
        (27, 'SLR',         'DMR',    '7.62mm',   51.45, 840.0, 0.200,
         'SKS의 후속 DMR. 더 높은 데미지와 반동을 가진다.',                           True,  url('SLR','DMR')),
        (28, 'Mk14 EBR',    'DMR',    '7.62mm',   55.56, 853.0, 0.150,
         '드랍 전용 DMR. 완전 연사 모드 지원.',                                       True,  url('Mk14 EBR','DMR')),
        (29, 'Dragunov',    'DMR',    '7.62mm',   55.56, 830.0, 0.330,
         '반자동 저격 DMR. 볼트액션보다 연사가 빠르다.',                              True,  url('Dragunov','DMR')),
        # ── LMG ─────────────────────────────────────────────────
        (30, 'MG3',         'LMG',    '7.62mm',   44.1,  820.0, 0.0606,
         '드랍 전용 LMG. 최고 연사속도를 자랑하는 경기관총.',                         True,  url('MG3','LMG')),
        (31, 'M249',        'LMG',    '5.56mm',   43.05, 915.0, 0.075,
         '100발 벨트 탄약의 LMG. 지속 화력에 강점.',                                  True,  url('M249','LMG')),
        # ── SR ──────────────────────────────────────────────────
        (32, 'AWM',         'SR',     '.300 Mag', 136.5, 954.0, 1.850,
         '드랍 전용 볼트액션 저격총. 레벨3 헬멧도 원샷.',                             False, url('AWM','SR')),
        (33, 'Kar98k',      'SR',     '7.62mm',   102.7, 785.0, 1.620,
         '클래식 볼트액션 저격총. 헤드샷 원샷 가능.',                                  False, url('Kar98k','SR')),
        (34, 'M24',         'SR',     '7.62mm',   97.5,  815.0, 1.520,
         'Kar98k보다 약간 빠른 볼트액션 저격총.',                                      False, url('M24','SR')),
        (35, 'Lynx AMR',    'SR',     '.50 BMG',  153.4, 1200.0,0.700,
         '드랍 전용 .50 BMG 대물 저격총. 차량에도 유효 타격.',                        False, url('Lynx AMR','SR')),
        # ── SG ──────────────────────────────────────────────────
        (36, 'S686',        'SG',     '12 Gauge', 26.0,  360.0, 0.200,
         '더블배럴 샷건. 근거리 순간 화력 최강.',                                      False, url('S686','SG')),
        (37, 'S1897',       'SG',     '12 Gauge', 26.0,  360.0, 0.750,
         '펌프액션 샷건. 안정적인 근거리 화력.',                                       False, url('S1897','SG')),
        (38, 'S12K',        'SG',     '12 Gauge', 24.0,  360.0, 0.250,
         '반자동 샷건. 빠른 연속 사격이 가능하다.',                                    False, url('S12K','SG')),
        (39, 'DBS',         'SG',     '12 Gauge', 26.0,  360.0, 0.133,
         '드랍 전용 이중 배럴 슬라이딩 샷건.',                                        False, url('DBS','SG')),
        (40, 'O12',         'SG',     '12 Gauge', 100.0, 625.0, 0.125,
         '드랍 전용 반자동 샷건. 매우 높은 피해량.',                                   False, url('O12','SG')),
        # ── Pistol ──────────────────────────────────────────────
        (41, 'P18C',        'Pistol', '9mm',      41.0,  375.0, 0.060,
         '완전 연사 가능 권총. 근거리 보조 화기.',                                     False, url('P18C','Pistol')),
        (42, 'P1911',       'Pistol', '.45 ACP',  41.0,  281.0, 0.110,
         '클래식 .45 ACP 권총. 높은 데미지.',                                          False, url('P1911','Pistol')),
        (43, 'R1895',       'Pistol', '7.62mm',   55.0,  330.0, 0.400,
         '7.62mm 리볼버. 매우 높은 데미지.',                                           False, url('R1895','Pistol')),
        (44, 'R45',         'Pistol', '.45 ACP',  55.0,  281.0, 0.250,
         '.45 ACP 리볼버. 강력한 스핀들.',                                             False, url('R45','Pistol')),
        (45, 'Deagle',      'Pistol', '.357 Mag', 62.0,  360.0, 0.250,
         '강력한 .357 Mag 권총.',                                                      False, url('Deagle','Pistol')),
        (46, 'Sawed-off',   'Pistol', '12 Gauge', 26.0,  360.0, 0.200,
         '소형 샷건 권총. 극근거리 전용.',                                             False, url('Sawed-off','Pistol')),
        (47, 'P92',         'Pistol', '9mm',      41.0,  375.0, 0.086,
         '표준 9mm 권총. 보조 화기로 무난하다.',                                       False, url('P92','Pistol')),
    ]

    conn.executemany(
        "INSERT INTO WEAPON VALUES (?,?,?,?,?,?,?,?,?,?)", weapons
    )


def _insert_attachments(conn):
    def url(n):
        return 'https://placehold.co/120x80/1a1f2e/4fc3f7?text=' + n.replace(' ','+')
    attachments = [
        (1,  '소음기',                'Muzzle',   url('소음기'),        -0.05,-0.05,-0.10,-0.15, 0.00, 0.00),
        (2,  '소염기',                'Muzzle',   url('소염기'),        -0.10,-0.10,-0.10,-0.10, 0.00, 0.00),
        (3,  '보정기',                'Muzzle',   url('보정기'),        -0.20,-0.15,-0.20, 0.00, 0.00, 0.00),
        (4,  '제동기',                'Muzzle',   url('제동기'),        -0.10,-0.08, 0.00,-0.80, 0.00, 0.00),
        (5,  '초크',                  'Muzzle',   url('초크'),           0.00, 0.00,-0.20,-0.20, 0.00, 0.00),
        (6,  '덕빌',                  'Muzzle',   url('덕빌'),           0.00,-1.00,-0.10,-0.10, 0.00, 0.00),
        (7,  '전술 개머리판',         'Stock',    url('전술 개머리판'),  0.00, 0.00,-0.25, 0.00,-0.20,-0.10),
        (8,  '중량형 개머리판',       'Stock',    url('중량형 개머리판'),-0.25,-0.25, 0.00, 0.00,-0.10, 0.00),
        (9,  '칙패드',                'Stock',    url('칙패드'),        -0.50, 0.00,-0.50,-0.50,-0.30, 0.00),
        (10, '경량형 개머리판',       'Stock',    url('경량형 개머리판'),-0.10, 0.00, 0.00, 0.00,-0.10, 0.00),
        (11, '탄띠',                  'Stock',    url('탄띠'),           0.00, 0.00, 0.00, 0.00, 0.30, 0.00),
        (12, '접이식 개머리판',       'Stock',    url('접이식 개머리판'),-0.40,-0.10, 0.00, 0.00,-0.20, 0.00),
        (13, '수직 손잡이',           'Grip',     url('수직 손잡이'),   -0.40, 0.00, 0.00, 0.00, 0.00, 0.00),
        (14, '라이트 그립',           'Grip',     url('라이트 그립'),    0.00, 0.00,-0.25, 0.00,-0.50,-0.80),
        (15, '엄지그립',              'Grip',     url('엄지그립'),      -0.25, 0.00, 0.00, 0.00,-0.25, 0.00),
        (16, '하프 그립',             'Grip',     url('하프 그립'),     -0.20,-0.40, 0.00, 0.00,-0.25, 0.00),
        (17, '틸티드 그립',           'Grip',     url('틸티드 그립'),   -0.30,-0.15, 0.00,-0.60, 0.00, 0.00),
        (18, '레이저 사이트',         'Grip',     url('레이저 사이트'),  0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (19, '대용량 탄창',           'Magazine', url('대용량 탄창'),    0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (20, '퀵 드로우 탄창',        'Magazine', url('퀵 드로우 탄창'), 0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (21, '대용량 퀵 드로우 탄창', 'Magazine', url('대퀵 탄창'),      0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (22, '캔티드 사이트',         'Scope',    url('캔티드'),         0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (23, '레드닷 조준경',         'Scope',    url('레드닷'),         0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (24, '홀로그래픽 조준경',     'Scope',    url('홀로그래픽'),     0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (25, '2배율 스코프',          'Scope',    url('2배율'),          0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (26, '3배율 스코프',          'Scope',    url('3배율'),          0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (27, '4배율 (ACOG) 스코프',   'Scope',    url('4배율ACOG'),      0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (28, '하이브리드 스코프',     'Scope',    url('하이브리드'),     0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (29, '6배율 스코프',          'Scope',    url('6배율'),          0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (30, '8배율 (CQBSS) 스코프',  'Scope',    url('8배율'),          0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
        (31, '15배율 (PM II) 스코프', 'Scope',    url('15배율'),         0.00, 0.00, 0.00, 0.00, 0.00, 0.00),
    ]
    conn.executemany("INSERT INTO ATTACHMENT VALUES (?,?,?,?,?,?,?,?,?,?)", attachments)

def _insert_recoils(conn):
    """
    WEAPON_RECOIL: 총기 종류·탄약 종류별 템플릿 기반으로 자동 계산.
    안정성 점수는 _calc_stability() 공식으로 산출.
    """
    # weapon 목록 가져오기
    rows = conn.execute(
        "SELECT weapon_id, gun_type, bullet_type, fire_speed FROM WEAPON ORDER BY weapon_id"
    ).fetchall()

    recoil_rows = []
    for rid, (wid, gtype, btype, fspeed) in enumerate(rows, start=1):
        v, h, pat, first, cr, pr, rise, shake, rec, vspd = _get_template(gtype, btype)

        # 총기별 미세 보정 (실제 게임 특성 반영)
        adj = _WEAPON_ADJ.get(wid, 1.0)
        v, h, rise, shake, first = (round(x * adj, 4) for x in (v, h, rise, shake, first))

        score, grade = _calc_stability(v, h, rise, shake, fspeed, gtype)
        recoil_rows.append((rid, wid, v, h, pat, first, cr, pr, rise, shake, rec, vspd, score, grade))

    conn.executemany(
        "INSERT INTO WEAPON_RECOIL VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", recoil_rows
    )


# 총기별 반동 보정 계수 (1.0 = 템플릿 그대로, <1.0 = 낮은 반동, >1.0 = 높은 반동)
_WEAPON_ADJ = {
    1:  0.90,   # M416     — 낮은 반동으로 유명
    2:  1.20,   # AKM      — 강한 반동
    3:  0.95,   # SCAR-L
    4:  0.88,   # M16A4    — 단발/3점사로 효과적 반동 낮음
    5:  1.15,   # Groza    — 강한 반동
    6:  0.85,   # AUG A3   — 에어드롭, 낮은 반동
    7:  1.10,   # Beryl    — 높은 반동
    8:  0.92,   # QBZ95
    9:  0.93,   # G36C
    10: 1.05,   # MK47
    11: 1.05,   # ACE32
    12: 0.88,   # FAMAS    — 3점사
    13: 0.93,   # K2
    14: 1.05,   # UMP45    — .45 ACP, 약간 높은 반동
    15: 1.20,   # Vector   — 빠른 연사, 높은 체감 반동
    16: 1.25,   # UZI      — 최고 연사, 강한 반동
    17: 0.95,   # Tommy Gun
    18: 0.95,   # MP5K
    19: 0.92,   # MP9
    20: 0.95,   # JS9
    21: 0.88,   # P90      — 낮은 반동
    22: 1.15,   # SKS      — 강한 반동 DMR
    23: 0.88,   # Mini 14  — 낮은 반동
    24: 0.90,   # VSS
    25: 0.90,   # QBU
    26: 0.92,   # MK12
    27: 1.20,   # SLR      — 강한 반동
    28: 1.10,   # Mk14 EBR
    29: 1.05,   # Dragunov
    30: 1.30,   # MG3      — 매우 빠른 연사
    31: 1.05,   # M249
}



def _insert_compat(conn):
    weapons = conn.execute(
        "SELECT weapon_id, gun_type, bullet_type FROM WEAPON ORDER BY weapon_id"
    ).fetchall()
    att_bonuses = {}
    for row in conn.execute(
        "SELECT attachment_id, slot_type, control_recoil_vertical, control_recoil_horizontal,"
        "       control_muzzle_rise, control_muzzle_shake, mod_recovery_recoil, control_first_recoil"
        " FROM ATTACHMENT"
    ).fetchall():
        att_bonuses[row[0]] = (row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    _SCALE = {
        '5.56mm':1.00,'7.62mm':1.30,'9mm':0.90,'5.7mm':0.85,
        '.45 ACP':1.10,'.300 Mag':1.80,'.50 BMG':2.00,
        '12 Gauge':0.80,'.357 Mag':1.20,
    }
    # 파츠 ID: 1=소음기 2=소염기 3=보정기 4=제동기 5=초크 6=덕빌
    #          7=전술개머리판 8=중량형 9=칙패드 10=경량형 11=탄띠 12=접이식
    #          13=수직손잡이 14=라이트 15=엄지 16=하프 17=틸티드 18=레이저
    #          19=대용량탄창 20=퀵드로우 21=대퀵 22=캔티드 23=레드닷 24=홀로
    #          25=2배 26=3배 27=4배ACOG 28=하이브리드 29=6배 30=8배 31=15배
    MAR  = [1,2,3,4];  MSR  = [1,2,3];  MSG  = [5];   MS12 = [1,3,4,5,6]; MO12 = [1,3,4]
    SAR  = [7,8,10];   SDM  = [9];      SSR  = [9,11]; SSG  = [11];       SUZ  = [12]
    G    = [13,14,15,16,17];            GL   = [13,14,15,16,17,18]
    MAG  = [19,20,21]; MAGS = [19,21]
    SCA  = [22,23,24,25,26,27,28,29];  SCAX = SCA+[30,31]
    SCM  = [22,23,24,25,26]
    SCD  = [22,23,24,25,26,27,28,29,30]; SCDX = SCD+[31]
    SCS  = [27,28,29,30,31];            SCSG = [22,23,24]
    SCL  = [22,23,24,25,26,27,28,29]
    _W = {
        1:  MAR+SAR+G+MAG+SCA,    2:  MAR+G+MAG+SCA,         3:  MAR+SAR+G+MAG+SCA,
        4:  MAR+SAR+G+MAG+SCAX,   5:  MAG+SCA,                6:  MAR+G+MAG+SCA,
        7:  MAR+G+MAG+SCA,         8:  MAR+SAR+G+MAG+SCA,     9:  MAR+SAR+G+MAG+SCA,
        10: MAR+SAR+G+MAG+SCAX,   11: MAR+SAR+G+MAG+SCA,     12: MAR+SAR+G+MAG+SCA,
        13: MAR+SAR+G+MAG+SCA,    14: MAR+SAR+GL+MAG+SCM,    15: MAR+SAR+GL+MAG+SCM,
        16: MSR+SUZ+MAG+SCM,      17: [1,2]+MAG+SCSG,         18: MAR+SAR+GL+MAG+SCM,
        19: MAR+SUZ+GL+MAG+SCM,   20: MAR+SAR+GL+MAG+SCM,    21: MSR+MAG+SCM,
        22: [1,2,3]+SDM+G+MAG+SCD,23: MAR+[9,10]+G+MAG+SCA+[30], 24: [22,23,24,25,26,27],
        25: MAR+[9,10]+G+MAG+SCA+[30], 26: MAR+SDM+G+MAG+SCDX, 27: [1,2,3]+SDM+G+MAG+SCD,
        28: MAR+SDM+G+MAG+SCDX,   29: [1,2]+[9]+SCS,
        30: SCL,                   31: [1,2]+SAR+G+[19,21]+SCL,
        32: [1]+SSR+MAGS+SCS,     33: MSR+SSR+SCS,            34: MSR+SSR+MAGS+SCS,
        35: SCS,
        36: MSG+SSG+SCSG,         37: MSG+SSG+SCSG,            38: MS12+MAG+SCSG,
        39: MSG+SCSG,             40: MO12+MAG+SCSG,
        41: [1]+MAG+SCSG,         42: MSR+SCSG,                43: SCSG,
        44: SCSG,                 45: MSR+SCSG,                46: [],
        47: [1]+MAG+SCSG,
    }
    rows = []; cid = 1
    for wid, gtype, btype in weapons:
        scale = _SCALE.get(btype, 1.0)
        for aid in _W.get(wid, []):
            if aid not in att_bonuses: continue
            _, v, h, rise, shake, rec, first = att_bonuses[aid]
            rows.append((cid, wid, aid,
                round(v*scale,4), round(h*scale,4), round(rise*scale,4),
                round(shake*scale,4), round(rec*scale,4), round(first*scale,4)))
            cid += 1
    conn.executemany("INSERT INTO WEAPON_ATTACHMENT_COMPAT VALUES (?,?,?,?,?,?,?,?,?)", rows)

# ═══════════════════════════════════════════════════════════════
# 진입점
# ═══════════════════════════════════════════════════════════════
def init_db():
    conn = duckdb.connect(DB_PATH)
    _create_tables(conn)
    _insert_weapons(conn)
    _insert_attachments(conn)
    _insert_recoils(conn)
    _insert_compat(conn)
    conn.close()
    print(f"[DB] 초기화 완료 → {DB_PATH}")


if __name__ == "__main__":
    init_db()


