from intelligence.main import Intelligence


def _candidate_with_cross(cross_score):
    return {
        "candidate_id": "cand_1",
        "cross_score": cross_score,
        "profile": {"years_of_experience": 7, "current_title": "Senior ML Engineer"},
        "skills": [{"name": "retrieval", "proficiency": "advanced", "endorsements": 20, "duration_months": 24}],
        "career_history": [
            {"title": "ML Engineer", "company": "A", "description": "retrieval systems"},
            {"title": "Senior ML Engineer", "company": "B", "description": "production ranking"},
        ],
        "redrob_signals": {
            "recruiter_response_rate": 0.7,
            "interview_completion_rate": 0.8,
            "offer_acceptance_rate": 0.6,
            "github_activity_score": 6,
            "profile_completeness_score": 90,
            "skill_assessment_scores": {"retrieval": 85},
        },
    }


def test_cross_score_conversion_handles_negative_raw_values_without_zeroing():
    result = Intelligence.score_candidate(_candidate_with_cross(-4.4))

    assert 0 < result["cross_score"] < 50


def test_cross_score_conversion_preserves_ordering_for_higher_raw_scores():
    low = Intelligence.score_candidate(_candidate_with_cross(-2.0))
    high = Intelligence.score_candidate(_candidate_with_cross(2.0))

    assert low["cross_score"] < high["cross_score"]
    assert low["overall_score"] < high["overall_score"]
