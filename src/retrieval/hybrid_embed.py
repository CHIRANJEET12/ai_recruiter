from retrieval.bm25_retrieval import BM25Ranker
from retrieval.embedding_retrieval import EmbeddingRanker
from jd_Parser.jd_parser import JDParser
from typing import Dict, List, Tuple

class HybridRetriever:
    def __init__(self):
        self.bm25_ranker = BM25Ranker()
        self.embedding_ranker = EmbeddingRanker()

    @staticmethod
    def normalize(scores) -> Dict[str, float]:

        values = list(scores.values())

        min_score = min(values)
        max_score = max(values)

        normalized = {}

        for cid, score in scores.items():

            normalized[cid] = (
                score - min_score
            ) / (
                max_score - min_score + 1e-9
            )

        return normalized

    def retrieve(
        self,
        jd_query: str,
        top_k=500,
        bm25_weight=0.5,
        embedding_weight=0.5
    ) -> List[Dict[str, str | float]]:
        
        bm25_results = self.bm25_ranker.rank(jd_query)

        bm25_scores = (
            self.bm25_ranker.get_score_dict(
                bm25_results
            )
        )

        embedding_results = (
            self.embedding_ranker.rank(
                jd_query
            )
        )

        embedding_scores = (
            self.embedding_ranker.get_score_dict(
                embedding_results
            )
        )

        bm25_norm = self.normalize(
            bm25_scores
        )

        embedding_norm = self.normalize(
            embedding_scores
        )

        hybrid_results = []

        for cid in bm25_norm:

            hybrid_score = (
                bm25_weight * bm25_norm[cid]
                +
                embedding_weight * embedding_norm[cid]
            )

            hybrid_results.append(
                {
                    "candidate_id": cid,
                    "hybrid_score": hybrid_score
                }
            )

        hybrid_results.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        return hybrid_results[:top_k]


if __name__ == "__main__":

    h_retriev = HybridRetriever()

    jd_query = JDParser.get_jd()
    
    hybrid_results = h_retriev.retrieve(jd_query,top_k=500)
