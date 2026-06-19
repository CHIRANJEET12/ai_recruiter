from ranking.rule_engine import RuleBasedReranker


def test_rule_engine_bumps_open_to_work_candidates():
    candidates = [
        {"candidate_id": "c1", "cross_score": 0.50, "redrob_signals": {"open_to_work_flag": True}},
        {"candidate_id": "c2", "cross_score": 0.50, "redrob_signals": {}},
    ]

    reranker = RuleBasedReranker()
    results = reranker.rerank(candidates, top_k=10)

    assert results[0]["candidate_id"] == "c1"
    assert results[0]["stage3_score"] > results[1]["stage3_score"]


def test_rule_engine_penalizes_long_notice_period():
    candidates = [
        {"candidate_id": "c1", "cross_score": 0.50, "redrob_signals": {"notice_period_days": 90}},
        {"candidate_id": "c2", "cross_score": 0.50, "redrob_signals": {"notice_period_days": 15}},
    ]

    reranker = RuleBasedReranker()
    results = reranker.rerank(candidates, top_k=10)

    assert results[0]["candidate_id"] == "c2"
    assert results[0]["stage3_score"] > results[1]["stage3_score"]


def test_rule_engine_handles_missing_redrob_signals_gracefully():
    candidates = [
        {"candidate_id": "c1", "cross_score": 0.50},
        {"candidate_id": "c2", "cross_score": 0.30},
    ]

    reranker = RuleBasedReranker()
    results = reranker.rerank(candidates, top_k=10)

    assert len(results) == 2
    assert results[0]["candidate_id"] == "c1"
    assert "stage3_score" in results[0]


def test_rule_engine_combines_multiple_signals_correctly():
    strong = {
        "candidate_id": "strong",
        "cross_score": 0.50,
        "redrob_signals": {
            "open_to_work_flag": True,
            "willing_to_relocate": True,
            "recruiter_response_rate": 0.8,
            "notice_period_days": 14,
            "last_active_date": "2026-06-01",
        },
    }
    weak = {
        "candidate_id": "weak",
        "cross_score": 0.50,
        "redrob_signals": {
            "open_to_work_flag": False,
            "willing_to_relocate": False,
            "recruiter_response_rate": 0.2,
            "notice_period_days": 90,
            "last_active_date": "2025-01-01",
        },
    }

    reranker = RuleBasedReranker()
    results = reranker.rerank([weak, strong], top_k=10)

    assert results[0]["candidate_id"] == "strong"
    assert results[0]["stage3_score"] > 0.50
    assert results[1]["stage3_score"] < 0.50
