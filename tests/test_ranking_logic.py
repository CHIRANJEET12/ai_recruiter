import math

from jd_understanding.schemas import ScoreWeights
from ranking.main import RankingEngine
from ranking.reasoning import ReasonGenerator
from ranking.schemas import CandidateComponentScores
from ranking.scoring import FinalRankCalculator, ScoreNormalizer


def test_score_normalizer_handles_missing_components_and_constant_values():
    candidates = [
        CandidateComponentScores(candidate_id="c1", cross_score=0.9, experience_score=7.0),
        CandidateComponentScores(candidate_id="c2", cross_score=0.8, experience_score=7.0),
        CandidateComponentScores(candidate_id="c3", cross_score=0.7, experience_score=None),
    ]

    normalized = ScoreNormalizer.normalize_candidates(candidates)

    assert math.isclose(normalized["c1"]["cross"], 1.0, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(normalized["c3"]["cross"], 0.0, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(normalized["c1"]["experience"], 0.5, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(normalized["c2"]["experience"], 0.5, rel_tol=0, abs_tol=1e-9)
    assert "experience" not in normalized["c3"]


def test_final_rank_calculator_renormalizes_when_component_is_missing():
    weights = ScoreWeights(cross=0.4, experience=0.3, behavior=0.1, evidence=0.1, trajectory=0.1)
    candidate = CandidateComponentScores(candidate_id="c1", cross_score=0.8, experience_score=None)
    normalized_scores = {"cross": 0.8}

    result = FinalRankCalculator.calculate(candidate, normalized_scores, weights)

    assert math.isclose(result["final_score"], 0.8, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(result["cross"], 0.8, rel_tol=0, abs_tol=1e-9)


def test_ranking_engine_sorts_by_final_score_and_generates_reasoning():
    from jd_understanding.schemas import ParsedJD

    parsed_jd = ParsedJD(seniority="senior", years_required=5, role_family="search")
    candidates = [
        CandidateComponentScores(
            candidate_id="cand_b",
            cross_score=0.40,
            experience_score=0.70,
            behavior_score=0.50,
            evidence_score=0.60,
            trajectory_score=0.50,
        ),
        CandidateComponentScores(
            candidate_id="cand_a",
            cross_score=0.95,
            experience_score=0.90,
            behavior_score=0.70,
            evidence_score=0.80,
            trajectory_score=0.85,
        ),
        CandidateComponentScores(
            candidate_id="cand_c",
            cross_score=0.20,
            experience_score=0.35,
            behavior_score=0.30,
            evidence_score=0.25,
            trajectory_score=0.20,
        ),
    ]

    ranked = RankingEngine.rank(parsed_jd, candidates)

    assert [item.candidate_id for item in ranked] == ["cand_a", "cand_b", "cand_c"]
    assert ranked[0].final_score >= ranked[1].final_score >= ranked[2].final_score
    assert ranked[0].reasoning.startswith("Strong ")


def test_reason_generator_returns_professional_headline_and_caveat():
    reasoning = ReasonGenerator.generate(
        {
            "cross": 0.92,
            "experience": 0.88,
            "behavior": 0.72,
            "evidence": 0.40,
            "trajectory": 0.84,
        }
    )

    assert "Strong retrieval relevance" in reasoning
    assert "Relative gap in evidence strength" in reasoning
