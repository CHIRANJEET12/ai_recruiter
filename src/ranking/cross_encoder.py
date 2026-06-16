from sentence_transformers import CrossEncoder

class CrossEncoderRanker:
    def __init__(self):

        print("Loading Cross Encoder...")

        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, jd_query, retrieved_candidates, top_k=100):

        pairs = []

        for candidate in retrieved_candidates:
            pairs.append([jd_query, candidate["text"]])

        scores = self.model.predict(pairs, show_progress_bar=True)

        results = []

        for candidate, score in zip(retrieved_candidates, scores):
            results.append({
                "candidate_id":
                    candidate["candidate_id"],

                "cross_score":
                    float(score),

                "text":
                    candidate["text"]
            })

        results.sort(
            key = lambda x : x["cross_score"],
            reverse=True
        )

        return results[:top_k]