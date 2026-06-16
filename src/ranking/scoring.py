from __future__ import annotations

from typing import Dict, Iterable, List

from jd_understanding.schemas import ScoreWeights
from ranking.schemas import CandidateComponentScores


COMPONENT_KEYS = ("cross", "experience", "behavior", "evidence", "trajectory")


class ScoreNormalizer:
    @staticmethod
    def _min_max(values: List[float]) -> List[float]:
        if not values:
            return []
        v_min = min(values)
        v_max = max(values)
        if abs(v_max - v_min) < 1e-9:
            return [0.5 for _ in values]
        return [(v - v_min) / (v_max - v_min) for v in values]

    @classmethod
    def normalize_candidates(
        cls, candidates: Iterable[CandidateComponentScores]
    ) -> Dict[str, Dict[str, float]]:
        candidates_list = list(candidates)
        normalized_by_id: Dict[str, Dict[str, float]] = {
            candidate.candidate_id: {} for candidate in candidates_list
        }

        for component in COMPONENT_KEYS:
            present = []
            present_ids = []
            for candidate in candidates_list:
                value = candidate.as_dict()[component]
                if value is not None:
                    present.append(float(value))
                    present_ids.append(candidate.candidate_id)

            normalized_values = cls._min_max(present)
            for idx, candidate_id in enumerate(present_ids):
                normalized_by_id[candidate_id][component] = normalized_values[idx]

        return normalized_by_id


class FinalRankCalculator:
    @staticmethod
    def _renormalize_weights(weights: ScoreWeights, available_components: List[str]) -> Dict[str, float]:
        base = weights.to_dict()
        filtered = {k: base[k] for k in available_components}
        total = sum(filtered.values())
        if total <= 0:
            return {k: 1.0 / len(available_components) for k in available_components}
        return {k: v / total for k, v in filtered.items()}

    @classmethod
    def calculate(
        cls,
        candidate: CandidateComponentScores,
        normalized_scores: Dict[str, float],
        weights: ScoreWeights,
    ) -> Dict[str, float]:
        available_components = [key for key in COMPONENT_KEYS if key in normalized_scores]
        if not available_components:
            return {"final_score": 0.0}

        effective_weights = cls._renormalize_weights(weights, available_components)
        final_score = sum(normalized_scores[key] * effective_weights[key] for key in available_components)
        output = {"final_score": final_score}
        for key in COMPONENT_KEYS:
            if key in normalized_scores:
                output[key] = normalized_scores[key]
        return output
