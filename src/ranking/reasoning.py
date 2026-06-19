from __future__ import annotations

from typing import Dict, List, Tuple


COMPONENT_READABLE = {
    "cross": "retrieval relevance",
    "experience": "experience alignment",
    "behavior": "behavior reliability",
    "evidence": "evidence strength",
    "trajectory": "career trajectory",
}


class ReasonGenerator:
    @staticmethod
    def _top_and_bottom_components(breakdown: Dict[str, float]) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
        scored = [(k, v) for k, v in breakdown.items() if k in COMPONENT_READABLE]
        scored.sort(key=lambda item: item[1], reverse=True)
        top = scored[:3]
        bottom = scored[-1:] if scored else []
        return top, bottom

    @classmethod
    def generate(cls, score_breakdown: Dict[str, float]) -> str:
        top_components, weakest_component = cls._top_and_bottom_components(score_breakdown)

        if not top_components:
            return "Insufficient component scores to generate recruiter reasoning."

        top_phrases = [COMPONENT_READABLE[name] for name, _ in top_components[:2]]
        if len(top_phrases) == 1:
            headline = f"Strong {top_phrases[0]}."
        else:
            headline = f"Strong {top_phrases[0]} and {top_phrases[1]}."

        caveat = ""
        if weakest_component:
            weak_name, weak_value = weakest_component[0]
            if weak_value < 0.45:
                caveat = f" Relative gap in {COMPONENT_READABLE[weak_name]}."

        return headline + caveat
