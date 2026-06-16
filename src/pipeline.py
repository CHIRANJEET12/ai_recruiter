from jd_parser import JDParser
from jd_understanding.parser import JDParserEngine
from ranking.main import RankingEngine
from ranking.schemas import CandidateComponentScores
from retrieval.hybrid_embed import HybridRetriever

jd = JDParser.get_jd()

parsed_jd = JDParserEngine.parse(jd)

retrieve = HybridRetriever()

top_candidates = retrieve.retrieve(jd, top_k=500)

component_scores = [
    CandidateComponentScores(
        candidate_id=candidate["candidate_id"],
        cross_score=candidate["hybrid_score"],
        experience_score=None,
        behavior_score=None,
        evidence_score=None,
        trajectory_score=None,
    )
    for candidate in top_candidates
]

final_ranked = RankingEngine.rank(parsed_jd, component_scores)

for candidate in final_ranked[:10]:
    print(
                f"{candidate.candidate_id} "
                f"{round(candidate.final_score, 4)} "
                f"| {candidate.reasoning}"
            )



# top_500 = retriever.retrieve(jd)

# top_100 = reranker.rerank(
#     jd,
#     top_500
# )

# final_ranked = intelligence.score(
#     top_100
# )
