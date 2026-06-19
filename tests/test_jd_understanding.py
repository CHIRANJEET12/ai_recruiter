import math

import pytest

from jd_understanding.parser import JDParserEngine
from jd_understanding.policy import WeightPolicyEngine
from jd_understanding.schemas import ParsedJD


def test_parse_extracts_required_preferred_seniority_years_and_role_family():
    raw_jd = """
    Senior AI Search Engineer
    Need: Retrieval, Ranking, Vector DB, 5+ years
    Preferred: NLP, A/B Testing
    """

    parsed = JDParserEngine.parse(raw_jd)

    assert parsed.seniority == "senior"
    assert parsed.years_required == 5
    assert parsed.role_family == "search"
    assert "information retrieval" in parsed.required_skills
    assert "ranking" in parsed.required_skills
    assert "vector databases" in parsed.required_skills
    assert "nlp" in parsed.preferred_skills
    assert "a/b testing" in parsed.preferred_skills


@pytest.mark.parametrize(
    "title, expected_seniority",
    [
        ("Principal AI Architect", "principal"),
        ("Staff ML Engineer", "staff"),
        ("Senior Search Engineer", "senior"),
        ("Junior ML Engineer", "junior"),
    ],
)
def test_parse_detects_seniority_from_title(title, expected_seniority):
    parsed = JDParserEngine.parse(title)
    assert parsed.seniority == expected_seniority


def test_weight_policy_prioritizes_experience_for_principal_architect():
    parsed = ParsedJD(
        required_skills=["python", "ranking"],
        preferred_skills=[],
        seniority="principal",
        years_required=10,
        role_family="search",
    )

    weights = WeightPolicyEngine.get_weights(parsed).to_dict()

    assert math.isclose(sum(weights.values()), 1.0, rel_tol=0, abs_tol=1e-9)
    assert weights["experience"] > weights["cross"]
    assert weights["trajectory"] > weights["behavior"]


def test_weight_policy_prioritizes_skills_for_junior_ml_engineer():
    parsed = ParsedJD(
        required_skills=["python", "embeddings"],
        preferred_skills=[],
        seniority="junior",
        years_required=1,
        role_family="general",
    )

    weights = WeightPolicyEngine.get_weights(parsed).to_dict()

    assert math.isclose(sum(weights.values()), 1.0, rel_tol=0, abs_tol=1e-9)
    assert weights["cross"] > weights["experience"]
    assert weights["evidence"] >= weights["trajectory"]
