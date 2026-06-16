from __future__ import annotations

from jd_understanding.schemas import ParsedJD, ScoreWeights


class WeightPolicyEngine:
    BASE_BY_SENIORITY = {
        "junior": ScoreWeights(cross=0.40, experience=0.15, behavior=0.15, evidence=0.20, trajectory=0.10),
        "mid": ScoreWeights(cross=0.36, experience=0.20, behavior=0.14, evidence=0.18, trajectory=0.12),
        "senior": ScoreWeights(cross=0.34, experience=0.25, behavior=0.12, evidence=0.15, trajectory=0.14),
        "staff": ScoreWeights(cross=0.28, experience=0.30, behavior=0.13, evidence=0.11, trajectory=0.18),
        "principal": ScoreWeights(cross=0.24, experience=0.32, behavior=0.12, evidence=0.10, trajectory=0.22),
        "unknown": ScoreWeights(cross=0.33, experience=0.24, behavior=0.13, evidence=0.16, trajectory=0.14),
    }

    @staticmethod
    def _apply_role_family_adjustments(parsed_jd: ParsedJD, weights: ScoreWeights) -> ScoreWeights:
        adjusted = weights.to_dict()

        if parsed_jd.role_family == "search":
            adjusted["cross"] += 0.03
            adjusted["experience"] += 0.01
            adjusted["evidence"] -= 0.02
            adjusted["behavior"] -= 0.01

        if parsed_jd.role_family == "ml_platform":
            adjusted["experience"] += 0.03
            adjusted["trajectory"] += 0.02
            adjusted["cross"] -= 0.03
            adjusted["evidence"] -= 0.02

        if parsed_jd.role_family == "backend_ai":
            adjusted["experience"] += 0.02
            adjusted["behavior"] += 0.01
            adjusted["cross"] -= 0.02
            adjusted["evidence"] -= 0.01

        if parsed_jd.years_required >= 8:
            adjusted["experience"] += 0.04
            adjusted["trajectory"] += 0.02
            adjusted["cross"] -= 0.03
            adjusted["evidence"] -= 0.03
        elif parsed_jd.years_required <= 2 and parsed_jd.years_required > 0:
            adjusted["cross"] += 0.03
            adjusted["evidence"] += 0.02
            adjusted["experience"] -= 0.03
            adjusted["trajectory"] -= 0.02

        return ScoreWeights(**adjusted)

    @classmethod
    def get_weights(cls, parsed_jd: ParsedJD) -> ScoreWeights:
        base = cls.BASE_BY_SENIORITY.get(parsed_jd.seniority, cls.BASE_BY_SENIORITY["unknown"])
        return cls._apply_role_family_adjustments(parsed_jd, base)
