import json
import csv
import pickle
import math

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SUBMISSION_DIR = ROOT_DIR / "submission"

SUBMISSION_DIR.mkdir(exist_ok=True)

from .experience import calculate_experience_score
from .behavior import calculate_behavior_score
from .career_match import calculate_career_match_score
from .evidence import calculate_evidence_score
from .honeypot import calculate_honeypot_score
from .trajectory import calculate_trajectory_score
from pipeline.candidate_repository import CandidateRepository
from common.paths import resolve_corpus_path


class Intelligence:

    def __init__(self, corpus_path=None):
        resolved_corpus_path = str(resolve_corpus_path()) if corpus_path is None else corpus_path
        self.respository = CandidateRepository(resolved_corpus_path)
    
    @staticmethod
    def _to_percent_score(raw_score):
        value = float(raw_score)
        probability = 1.0 / (1.0 + math.exp(-value))
        return probability * 100.0

    @staticmethod
    def score_candidate(candidate):
        experience_score = calculate_experience_score(candidate)
        career_match_score = calculate_career_match_score(candidate)
        evidence_score = calculate_evidence_score(candidate)
        behavior_score = calculate_behavior_score(candidate)
        trajectory_score = calculate_trajectory_score(candidate)
        honeypot_score = calculate_honeypot_score(candidate)
        cross_score_raw = candidate.get("cross_score", 0)
        cross_score = Intelligence._to_percent_score(cross_score_raw)

        overall_score = round(
            (
                career_match_score * 0.40
                +
                evidence_score * 0.25
                +
                behavior_score * 0.10
                +
                experience_score * 0.10
                +
                trajectory_score * 0.05
                +
                (100 - honeypot_score) * 0.10
                +
                cross_score
            ),
            2
        )        
        
        if career_match_score < 20:
            overall_score = overall_score * 0.50

        return {
            "candidate_id": candidate["candidate_id"],
            "overall_score": overall_score,
            "experience_score": experience_score,
            "career_match_score": career_match_score,
            "evidence_score": evidence_score,
            "behavior_score": behavior_score,
            "trajectory_score": trajectory_score,
            "honeypot_score": honeypot_score,
            "cross_score": round(cross_score, 2)
        }

class Save_data:
    @staticmethod
    def save_json(results):

        with open(
            SUBMISSION_DIR / "candidate_scores.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                results,
                f,
                indent=4
            )

    @staticmethod
    def save_csv(results):

        with open(
            SUBMISSION_DIR / "candidate_scores.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "candidate_id",
                    "overall_score",
                    "experience_score",
                    "career_match_score",
                    "evidence_score",
                    "behavior_score",
                    "trajectory_score",
                    "honeypot_score",
                    "cross_score"
                ]
            )

            writer.writeheader()

            writer.writerows(results)

class Intelligence_Run:

    def __init__(self, corpus_path=None):
        self.score = Intelligence(corpus_path=corpus_path)
        self.save = Save_data()
    
    def run(self, candidates):

        all_scores = []

        data_map = self.score.respository.getallEnrichedCandidates()

        # data_map = {
        #     candidate["candidate_id"] : candidate for candidate in data
        # }

        for candidate in candidates:

            candidate_data = data_map.get(candidate["candidate_id"])

            if candidate_data is None:
                continue

            merged_candidate = {
                **data_map[candidate["candidate_id"]],
                **candidate
            }

            result = self.score.score_candidate(
                merged_candidate
            )

            all_scores.append(
                result
            )

        all_scores.sort(
            key=lambda x:
            x["overall_score"],
            reverse=True
        )

        self.save.save_json(all_scores)

        self.save.save_csv(all_scores)

        return all_scores


# if __name__ == "__main__":

#     with open("../../data/candidate_corpus.pkl", "rb") as f:
#         candidates = pickle.load(f) 



#     i = Intelligence_Run()

#     result = i.run(candidates)

#     for res in result:
#         print(res)

