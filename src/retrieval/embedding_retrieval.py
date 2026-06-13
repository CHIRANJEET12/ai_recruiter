import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from jd_parser import JDParser

jd = JDParser.get_jd()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"


class EmbeddingRanker:
    def __init__(self):
        with open(DATA_DIR / "candidate_corpus.pkl", "rb") as f:
            self.candidate_corpus = pickle.load(f)

        with open(DATA_DIR / "candidate_ids.pkl", "rb") as f:
            self.ids = pickle.load(f)

        self.candidate_embeddings = np.load(
            DATA_DIR / "candidate_embeddings.npy"
        )

        print("\nLoading Embedding Model...\n")

        self.model = SentenceTransformer(
            "BAAI/bge-base-en-v1.5"
        )

        print("\nCreating Candidate Embeddings...\n")

        print(
            f"\nEmbedding Shape: "
            f"{self.candidate_embeddings.shape}"
        )

    def rank(self, jd_query):
        print("\nEmbedding Job Description...\n")

        query_embedding = self.model.encode(
            jd_query,
            normalize_embeddings=True
        )

        similarities = cosine_similarity(
            [query_embedding],
            self.candidate_embeddings
        )[0]

        results = []

        for idx, score in enumerate(similarities):
            results.append(
                {
                    "candidate_id":
                        self.candidate_corpus[idx]["candidate_id"],

                    "embedding_score":
                        float(score)
                }
            )

        results.sort(
            key=lambda x: x["embedding_score"],
            reverse=True
        )

        return results

    @staticmethod
    def get_score_dict(results):
        embedding_scores = {
            r["candidate_id"]: r["embedding_score"]
            for r in results
        }

        print(
            f"\nStored "
            f"{len(embedding_scores)} embedding scores."
        )

        return embedding_scores


class CandidateViewer:
    @staticmethod
    def show_top_candidates(results, top_k=10):
        print(f"\nTop {top_k} Candidates\n")

        for r in results[:top_k]:
            print(
                f"{r['candidate_id']} "
                f"{round(r['embedding_score'], 4)}"
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

                print(
                    f"Candidate ID: "
                    f"{candidate['candidate_id']}"
                )

                print("-" * 100)

                print(candidate["text"][:2000])

                print()


class CandidateRanker:
    def __init__(self):

        self.ranker = EmbeddingRanker()

        



    def run(self):
        jd_query = JDParser.get_jd()

        results = self.ranker.rank(jd_query)

        embedding_scores = (
            self.ranker.get_score_dict(results)
        )

        CandidateViewer.show_top_candidates(
            results,
            top_k=10
        )

        CandidateViewer.show_profiles(
            self.ranker.candidate_corpus,
            results,
            top_k=3
        )

        return results, embedding_scores


if __name__ == "__main__":
    candidate_ranker = CandidateRanker()

    results, embedding_scores = (
        candidate_ranker.run()
    )