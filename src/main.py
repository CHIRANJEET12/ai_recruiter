from pipeline.pipeline import Pipeline
from ranking.cross_encoder import CrossEncoderRanker

if __name__ == "__main__":

    print("Initializing system components...")
    shared_ranker = CrossEncoderRanker()
    pipeline = Pipeline(
        final_ranker=shared_ranker,
        retrieval_k=500,
        rerank_k=100,
    )

    final_results = pipeline.run()

    print("\n--- Final Ranking Summary ---")
    for r in final_results[:10]:
        print(
            f"{r.candidate_id:20s}  "
            f"{r.final_score:.4f}  "
            f"{r.reasoning}"
        )
