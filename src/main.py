from pipeline.pipeline import Pipeline
from ranking.cross_encoder import CrossEncoderRanker
from pipeline.timmer import Timer

timer = Timer()

if __name__ == "__main__":

    timer.start()

    print("Initializing system components...")
    shared_ranker = CrossEncoderRanker()
    pipeline = Pipeline(
        final_ranker=shared_ranker,
        retrieval_k=500,
        rerank_k=100,
    )

    final_results = pipeline.run()

    duration = timer.end()

    print(f"Total pipeline time Elapsed: {duration} s")


