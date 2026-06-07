from database import Database


def _calc_stability(vert, horiz, rise, shake, fire_speed, gun_type):
    """
    설계서 10절 공식 (fire_speed 단위: 초/발)
      per_shot    = min((vert+horiz+rise+shake)/2, 4.0)
      fire_recoil = per_shot * 1.2 / fire_speed   (≡ per_shot * RPM/50, RPM=60/fire_speed)
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


class CustomService:

    def __init__(self, config_repo, result_repo, query_repo, compat_repo, db: Database):
        self.config_repo = config_repo
        self.result_repo = result_repo
        self.query_repo = query_repo
        self.compat_repo = compat_repo
        self.db = db

    # ── 반동 계산 ─────────────────────────────────────────────────
    def calculate_recoil(self, weapon_id: int, slots: dict) -> dict:
        """
        기본 반동 + 장착 파츠의 총기별 보정값을 적용해 최종 반동 산출.
        slots = {muzzle, stock, grip, magazine, scope, foregrip} → attachment_id or None
        """
        base_df = self.db.q(
            "SELECT * FROM WEAPON_RECOIL WHERE weapon_id=?", [weapon_id]
        )
        if base_df.empty:
            return {}
        b = base_df.iloc[0]

        w_df = self.db.q("SELECT gun_type, fire_speed FROM WEAPON WHERE weapon_id=?", [weapon_id])
        if w_df.empty:
            return {}
        gun_type = w_df.iloc[0]['gun_type']
        fire_speed = float(w_df.iloc[0]['fire_speed'] or 0)

        vert     = float(b['recoil_vertical']   or 0)
        horiz    = float(b['recoil_horizontal']  or 0)
        rise     = float(b['muzzle_rise']        or 0)
        shake    = float(b['muzzle_shake']       or 0)
        first    = float(b['first_recoil']       or 0)
        recovery = float(b['recovery_recoil']    or 0)

        for att_id in [v for v in slots.values() if v is not None]:
            c_df = self.db.q(
                """SELECT * FROM WEAPON_ATTACHMENT_COMPAT
                   WHERE weapon_id=? AND attachment_id=?""",
                [weapon_id, att_id]
            )
            if c_df.empty:
                continue
            c = c_df.iloc[0]
            vert     += float(c['control_recoil_vertical']   or 0)
            horiz    += float(c['control_recoil_horizontal']  or 0)
            rise     += float(c['control_muzzle_rise']        or 0)
            shake    += float(c['control_muzzle_shake']       or 0)
            first    += float(c['control_first_recoil']       or 0)
            recovery += float(c['mod_recovery_recoil']        or 0)

        vert, horiz, rise, shake = (max(0.0, v) for v in (vert, horiz, rise, shake))
        first = max(0.0, first)

        score, grade = _calc_stability(vert, horiz, rise, shake, fire_speed, gun_type)

        return {
            'final_recoil_vertical':   round(vert, 4),
            'final_recoil_horizontal': round(horiz, 4),
            'final_muzzle_rise':       round(rise, 4),
            'final_muzzle_shake':      round(shake, 4),
            'final_first_shot_recoil': round(first, 4),
            'final_recoil_recovery':   round(recovery, 4),
            'stability_score':         score,
            'stability_grade':         grade,
        }

    # ── 저장 ──────────────────────────────────────────────────────
    def save_custom(self, weapon_id: int, custom_name: str, slots: dict) -> int:
        config_id = self.config_repo.save_config(weapon_id, custom_name, slots)
        result = self.calculate_recoil(weapon_id, slots)
        self.result_repo.save_result(config_id, result)
        return config_id

    # ── 조회 ──────────────────────────────────────────────────────
    def get_all_configs(self):
        return self.config_repo.find_all_with_weapon_name()

    def get_compat_by_slot(self, weapon_id: int, slot_type: str):
        return self.compat_repo.find_by_weapon_and_slot(weapon_id, slot_type)

    # ── 삭제 ──────────────────────────────────────────────────────
    def delete_config(self, config_id: int):
        self.result_repo.delete_by_config_id(config_id)
        self.config_repo.delete_by_id(config_id)

