import pickle
from rank_bm25 import BM25Okapi
import sys
from pathlib import Path
from typing import List, Dict, Tuple
sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from jd_Parser.jd_parser import JDParser
from common.paths import resolve_data_dir

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = resolve_data_dir()


class BM25Ranker:

    def __init__(self):

        print("\nLoading Candidate Corpus...\n")

        with open(DATA_DIR / "candidate_corpus.pkl", "rb") as f:
            self.candidate_corpus = pickle.load(f)

        self.ids = pickle.load(
            open(DATA_DIR / "candidate_ids.pkl", "rb")
        )

        documents = [
            candidate["text"]
            for candidate in self.candidate_corpus
        ]

        tokenized_docs = [
            doc.lower().split()
            for doc in documents
        ]

        print("Building BM25 Index...\n")

        self.bm25 = BM25Okapi(tokenized_docs)

    def rank(self, query: str) -> List[Dict[str, float | str]]:

        query_tokens = query.lower().split()

        scores = self.bm25.get_scores(query_tokens)

        results = []

        for idx, score in enumerate(scores):

            results.append(
                {
                    "candidate_id": self.ids[idx],
                    "bm25_score": float(score)
                }
            )

        results.sort(
            key=lambda x: x["bm25_score"],
            reverse=True
        )

        return results

    @staticmethod
    def get_score_dict(results: List[Dict[str, str | float]]) -> Dict[str, float]:

        return {
            r["candidate_id"]: r["bm25_score"]
            for r in results
        }


class CandidateViewer:

    @staticmethod
    def show_top_candidates(results, top_k=10):

        print(f"\nTop {top_k} BM25 Candidates\n")

        for r in results[:top_k]:

            print(
                f"{r['candidate_id']} "
                f"{round(r['bm25_score'], 4)}"
            )

    @staticmethod
    def show_profiles(candidate_corpus, results, top_k=3):

        print(f"\nTop {top_k} Candidate Profiles\n")

        top_ids = {
            r["candidate_id"]
            for r in results[:top_k]
        }

        for candidate in candidate_corpus:

            if candidate["candidate_id"] in top_ids:

                print("=" * 100)
                print(candidate["candidate_id"])
                print(candidate["text"][:2000])


class CandidateRanker:

    def __init__(self):

        self.ranker = BM25Ranker()

    def run(self) -> Tuple[List[Dict[str, float | str]], Dict[str, float]]:

        jd_query = JDParser.get_jd()

        results = self.ranker.rank(jd_query)

        bm25_scores = (
            self.ranker.get_score_dict(results)
        )

        print(
            f"\nStored {len(bm25_scores)} BM25 scores."
        )

        CandidateViewer.show_top_candidates(
            results
        )

        CandidateViewer.show_profiles(
            self.ranker.candidate_corpus,
            results
        )

        return results, bm25_scores


if __name__ == "__main__":

    ranker = CandidateRanker()

    results, bm25_scores = ranker.run()
