from jd_Parser.jd_parser import JDParser
from retrieval.hybrid_embed import HybridRetriever
# from ranking.cross_encoder import CrossEncoderRanker
from intelligence.main import Intelligence_Run
from common.paths import resolve_corpus_path

from pipeline.candidate_repository import CandidateRepository
from pipeline.timmer import Timer

class Pipeline:

    ## non default -> default args
    def __init__(
        self,
        final_ranker,
        retrieval_k,
        rerank_k,
        corpus_path=None,
        retriever=None,
        intelligence_runner=None,
    ):

        self.retrieval_k = retrieval_k
        self.rerank_k = rerank_k

        resolved_corpus_path = str(resolve_corpus_path()) if corpus_path is None else corpus_path
        self.respository = CandidateRepository(resolved_corpus_path)
        self.retriever = retriever or HybridRetriever()
        self.reranker = final_ranker
        self.intelligence = intelligence_runner or Intelligence_Run(corpus_path=resolved_corpus_path)
        

    def getJobDescription(self):
        return JDParser.get_jd()
    
    def IntelligenceofCandidate(self, candidates):
        timer = Timer()
        timer.start()

        intelligence_extract_rank = self.intelligence.run(candidates)

        duration = timer.end()
        print(f"Intelligence Extract Time: {duration:.3f} sec")

        return intelligence_extract_rank

    
    def retrieveCandidates(self, jd):
        timer = Timer()
        timer.start()

        candidates = self.retriever.retrieve(jd, top_k=self.retrieval_k)
        
        duration = timer.end()
        print(f"Retrieval Time: {duration:.3f} sec")

        return candidates
    
    def passCandidate(self, retrieved_candidate):
        passCand = []

        for candidate in retrieved_candidate:
            data = self.respository.getallCandidates().get(candidate["candidate_id"])
            if data is None:
                continue

            passCand.append({
                "candidate_id": data["candidate_id"],
                "text": data["text"],
                "hybrid_score": candidate["hybrid_score"]
            })

        return passCand
    
    def rerankCandidates(self, jd, candidates):
        timer = Timer()
        timer.start()

        ranked = self.reranker.rerank(
            jd,
            candidates,
            top_k=self.rerank_k
        )

        duration = timer.end()
        print(f"Reranking Time: {duration:.3f} sec")

        return ranked
    
    def display_results(self, ranked_candidates, top_n=10):
        print("\n--- Top Ranked Candidates ---")

        for candidate in ranked_candidates[:top_n]:
            print(f"ID: {candidate} ")
    
    def run(self):
        timer = Timer()
        timer.start()

        jd = self.getJobDescription()
        retrieve = self.retrieveCandidates(jd)
        passCand = self.passCandidate(retrieve)
        reranker = self.rerankCandidates(jd, passCand)
        finalranked = self.IntelligenceofCandidate(reranker)


        self.display_results(finalranked)

        print(f"\nTotal Execution Time: {timer.end():.3f} sec")

        return finalranked

# if __name__ == "__main__":
#     p = Pipeline()
#     p.run()

#   intelligence paert left
    # final_ranked = intelligence.score(
    #     top_100
    # )
