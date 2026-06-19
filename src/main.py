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


