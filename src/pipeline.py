from jd_parser import JDParser
from retrieval.hybrid_embed import HybridRetriever

jd = JDParser.get_jd()

retrieve = HybridRetriever()

top_candidates = retrieve.retrieve(jd, top_k=500)

for candidate in top_candidates[:10]:
    print(
                f"{candidate['candidate_id']} "
                f"{round(candidate['hybrid_score'], 4)}"
            )



# top_500 = retriever.retrieve(jd)

# top_100 = reranker.rerank(
#     jd,
#     top_500
# )

# final_ranked = intelligence.score(
#     top_100
# )