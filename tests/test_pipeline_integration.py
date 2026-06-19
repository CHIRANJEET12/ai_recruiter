import json
import pickle

from pipeline.pipeline import Pipeline


class FakeRetriever:
    def retrieve(self, jd_query, top_k=500):
        return [{"candidate_id": "CAND_1", "hybrid_score": 0.83}]


class FakeRanker:
    def rerank(self, jd_query, candidates, top_k=100):
        return [
            {
                "candidate_id": candidate["candidate_id"],
                "cross_score": 0.91,
                "text": candidate["text"],
                "hybrid_score": candidate.get("hybrid_score", 0.0),
                "profile": candidate.get("profile"),
                "redrob_signals": candidate.get("redrob_signals"),
            }
            for candidate in candidates[:top_k]
        ]


def test_pipeline_stage_flow_with_ranked_candidate_output(tmp_path):
    corpus_path = tmp_path / "candidate_corpus.pkl"
    detailed_path = tmp_path / "sample_candidates.json"

    minimal_corpus = [{"candidate_id": "CAND_1", "text": "candidate text"}]
    enriched_candidate = [
        {
            "candidate_id": "CAND_1",
            "profile": {"years_of_experience": 7, "current_title": "Senior Search Engineer"},
            "skills": [{"name": "retrieval", "proficiency": "advanced", "endorsements": 25, "duration_months": 36}],
            "career_history": [
                {
                    "title": "ML Engineer",
                    "company": "X",
                    "description": "built retrieval and ranking systems",
                },
                {
                    "title": "Senior ML Engineer",
                    "company": "Y",
                    "description": "owned production search",
                },
            ],
            "redrob_signals": {
                "recruiter_response_rate": 0.7,
                "interview_completion_rate": 0.8,
                "offer_acceptance_rate": 0.6,
                "github_activity_score": 8,
                "profile_completeness_score": 90,
                "skill_assessment_scores": {"retrieval": 88},
                "open_to_work_flag": True,
                "willing_to_relocate": True,
                "notice_period_days": 15,
                "last_active_date": "2026-05-01",
            },
            "education": [],
            "certifications": [],
            "languages": [],
        }
    ]

    with open(corpus_path, "wb") as file:
        pickle.dump(minimal_corpus, file)

    with open(detailed_path, "w", encoding="utf-8") as file:
        json.dump(enriched_candidate, file)

    pipeline = Pipeline(
        final_ranker=FakeRanker(),
        retrieval_k=5,
        rerank_k=2,
        corpus_path=str(corpus_path),
        retriever=FakeRetriever(),
    )

    results = pipeline.run()

    assert len(results) == 1
    ranked = results[0]
    assert ranked.candidate_id == "CAND_1"
    assert isinstance(ranked.final_score, float)
    assert isinstance(ranked.score_breakdown, dict)
    assert "cross" in ranked.score_breakdown
    assert isinstance(ranked.reasoning, str)
    assert len(ranked.reasoning) > 10


def test_pipeline_outputs_recruiter_facing_reasoning(tmp_path):
    corpus_path = tmp_path / "candidate_corpus.pkl"
    detailed_path = tmp_path / "sample_candidates.json"

    minimal_corpus = [{"candidate_id": "CAND_1", "text": "some text"}]
    enriched_candidate = [
        {
            "candidate_id": "CAND_1",
            "profile": {"years_of_experience": 5, "current_title": "ML Engineer"},
            "skills": [{"name": "python", "proficiency": "advanced", "endorsements": 15, "duration_months": 24}],
            "career_history": [
                {"title": "ML Engineer", "company": "Co", "description": "built ML systems"},
            ],
            "redrob_signals": {
                "recruiter_response_rate": 0.5,
                "interview_completion_rate": 0.5,
                "offer_acceptance_rate": 0.5,
                "github_activity_score": 5,
                "profile_completeness_score": 70,
                "skill_assessment_scores": {},
            },
            "education": [],
            "certifications": [],
            "languages": [],
        }
    ]

    with open(corpus_path, "wb") as file:
        pickle.dump(minimal_corpus, file)

    with open(detailed_path, "w", encoding="utf-8") as file:
        json.dump(enriched_candidate, file)

    pipeline = Pipeline(
        final_ranker=FakeRanker(),
        retrieval_k=5,
        rerank_k=2,
        corpus_path=str(corpus_path),
        retriever=FakeRetriever(),
    )

    results = pipeline.run()

    assert len(results) == 1
    assert results[0].reasoning.startswith("Strong ")
