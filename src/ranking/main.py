from __future__ import annotations

from typing import Iterable, List

from jd_understanding.policy import WeightPolicyEngine
from jd_understanding.schemas import ParsedJD
from ranking.reasoning import ReasonGenerator
from ranking.scoring import FinalRankCalculator, ScoreNormalizer
from ranking.schemas import CandidateComponentScores, RankedCandidate


class RankingEngine:
    @staticmethod
    def rank(
        parsed_jd: ParsedJD,
        candidates: Iterable[CandidateComponentScores],
    ) -> List[RankedCandidate]:
        candidates_list = list(candidates)
        weights = WeightPolicyEngine.get_weights(parsed_jd)
        normalized = ScoreNormalizer.normalize_candidates(candidates_list)

        ranked: List[RankedCandidate] = []
        for candidate in candidates_list:
            score_pack = FinalRankCalculator.calculate(
                candidate=candidate,
                normalized_scores=normalized.get(candidate.candidate_id, {}),
                weights=weights,
            )
            final_score = score_pack.pop("final_score", 0.0)
            reason = ReasonGenerator.generate(score_pack)
            ranked.append(
                RankedCandidate(
                    candidate_id=candidate.candidate_id,
                    final_score=round(final_score, 6),
                    score_breakdown=score_pack,
                    reasoning=reason,
                )
            )

        ranked.sort(
            key=lambda candidate: (
                -candidate.final_score,
                -candidate.score_breakdown.get("cross", 0.0),
                -candidate.score_breakdown.get("experience", 0.0),
                candidate.candidate_id,
            )
        )
        return ranked
