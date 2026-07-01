from jd_Parser.jd_parser import JDParser
from retrieval.hybrid_embed import HybridRetriever
from intelligence.main import Intelligence_Run
from common.paths import resolve_corpus_path
import pandas as pd

from pipeline.candidate_repository import CandidateRepository
from pipeline.timmer import Timer
from ranking.rule_engine import RuleBasedReranker
from ranking.main import RankingEngine
from ranking.schemas import CandidateComponentScores
from jd_understanding.parser import JDParserEngine

class Pipeline:

    def __init__(
        self,
        final_ranker,
        retrieval_k,
        rerank_k,
        corpus_path=None,
        retriever=None,
        intelligence_runner=None,
        rule_engine=None,
        ranking_engine=None,
    ):

        self.retrieval_k = retrieval_k
        self.rerank_k = rerank_k

        resolved_corpus_path = str(resolve_corpus_path()) if corpus_path is None else corpus_path
        print(resolved_corpus_path)
        self.respository = CandidateRepository(resolved_corpus_path)
        self.retriever = retriever or HybridRetriever()
        self.reranker = final_ranker
        self.intelligence = intelligence_runner or Intelligence_Run(corpus_path=resolved_corpus_path)
        self.rule_engine = rule_engine or RuleBasedReranker()
        self.ranking_engine = ranking_engine or RankingEngine

    def getJobDescription(self):
        return JDParser.get_jd()

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
            enriched = self.respository.getEnrichedCandidate(candidate["candidate_id"])
            if not enriched.get("text"):
                continue

            payload = {
                "candidate_id": enriched["candidate_id"],
                "text": enriched["text"],
                "hybrid_score": candidate.get("hybrid_score", 0.0),
            }
            profile = enriched.get("profile")
            if profile:
                payload["profile"] = profile
            signals = enriched.get("redrob_signals")
            if signals:
                payload["redrob_signals"] = signals
            skills = enriched.get("skills")
            if skills:
                payload["skills"] = skills
            career = enriched.get("career_history")
            if career:
                payload["career_history"] = career

            passCand.append(payload)

        return passCand

    def rerankCandidates(self, jd, candidates):
        timer = Timer()
        timer.start()

        ranked = self.reranker.rerank(jd, candidates, top_k=self.rerank_k)

        duration = timer.end()
        print(f"Reranking Time: {duration:.3f} sec")

        return ranked

    def runRuleEngine(self, candidates):
        timer = Timer()
        timer.start()

        reranked = self.rule_engine.rerank(candidates)

        duration = timer.end()
        print(f"Rule Engine Time: {duration:.3f} sec")

        return reranked

    def IntelligenceofCandidate(self, candidates):
        timer = Timer()
        timer.start()

        intelligence_extract_rank = self.intelligence.run(candidates)

        duration = timer.end()
        print(f"Intelligence Extract Time: {duration:.3f} sec")

        return intelligence_extract_rank

    def finalizeWithJDWeightedRankings(self, parsed_jd, intelligence_results):
        component_scores = []
        for item in intelligence_results:
            component_scores.append(
                CandidateComponentScores(
                    candidate_id=item["candidate_id"],
                    cross_score=item.get("cross_score", 50.0),
                    experience_score=item.get("experience_score"),
                    behavior_score=item.get("behavior_score"),
                    evidence_score=item.get("evidence_score"),
                    trajectory_score=item.get("trajectory_score"),
                )
            )

        ranked = self.ranking_engine.rank(parsed_jd, component_scores)
        return ranked

    def display_results(self, ranked_candidates, top_n=100):
        print("\n--- Top Ranked Candidates ---")
        for candidate in ranked_candidates[:top_n]:
            print(f"ID: {candidate.candidate_id}  Score: {candidate.final_score}  | {candidate.reasoning}")

    def run(self):
        timer = Timer()
        timer.start()

        jd = self.getJobDescription()
        parsed_jd = JDParserEngine.parse(jd)

        retrieve = self.retrieveCandidates(jd)
        passCand = self.passCandidate(retrieve)
        reranked = self.rerankCandidates(jd, passCand)
        rule_ranked = self.runRuleEngine(reranked)
        intelligence_results = self.IntelligenceofCandidate(rule_ranked)
        final_ranked = self.finalizeWithJDWeightedRankings(parsed_jd, intelligence_results)

        final_new_ranked = []

        for rank, candidate in enumerate(final_ranked, start=1):
            final_new_ranked.append({
                "candidate_id": candidate.candidate_id,
                "rank": rank,
                "score": candidate.final_score,
                "reasoning": candidate.reasoning
            })
            
        df = pd.DataFrame(final_new_ranked)

        df.to_csv(
            "submission.csv",
            index=False
        )
        print("Saved to submission.csv")

        self.display_results(final_ranked)

        print(f"\nTotal Execution Time: {timer.end():.3f} sec")

        return final_ranked

# if __name__ == "__main__":
#     p = Pipeline()
#     p.run()

#   intelligence paert left
    # final_ranked = intelligence.score(
    #     top_100
    # )
