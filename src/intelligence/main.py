import json
import csv
import pickle

from experience import (
    calculate_experience_score
)

from behavior import (
    calculate_behavior_score
)

from evidence import (
    calculate_evidence_score
)

from trajectory import (
    calculate_trajectory_score
)

from career_match import (
    calculate_career_match_score
)

from honeypot import (
    calculate_honeypot_score
)


def score_candidate(candidate):

    experience_score = (
        calculate_experience_score(
            candidate
        )
    )

    career_match_score = (
        calculate_career_match_score(
            candidate
        )
    )

    evidence_score = (
        calculate_evidence_score(
            candidate
        )
    )

    behavior_score = (
        calculate_behavior_score(
            candidate
        )
    )

    trajectory_score = (
        calculate_trajectory_score(
            candidate
        )
    )

    honeypot_score = (
        calculate_honeypot_score(
            candidate
        )
    )

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
    ),
    2
)
    if career_match_score < 20:

        overall_score = overall_score * 0.50

    return {
        "candidate_id":
            candidate["candidate_id"],

        "overall_score":
            overall_score,

        "experience_score":
            experience_score,

        "career_match_score":
            career_match_score,

        "evidence_score":
            evidence_score,

        "behavior_score":
            behavior_score,

        "trajectory_score":
            trajectory_score,

        "honeypot_score":
            honeypot_score
    }


def save_json(results):

    with open(
        "candidate_scores.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=4
        )


def save_csv(results):

    with open(
        "candidate_scores.csv",
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
                "honeypot_score"
            ]
        )

        writer.writeheader()

        writer.writerows(results)


if __name__ == "__main__":

    with open(
        "../../data/candidate_corpus.pkl",
        "rb"
    ) as f:

        candidates = pickle.load(f)

    all_scores = []

    for candidate in candidates:

        result = score_candidate(
            candidate
        )

        all_scores.append(
            result
        )

    all_scores.sort(
        key=lambda x:
        x["overall_score"],
        reverse=True
    )

    save_json(all_scores)

    save_csv(all_scores)

    print(
        f"\nProcessed "
        f"{len(all_scores)} candidates\n"
    )

    candidate_map = {
        candidate["candidate_id"]: candidate
        for candidate in candidates
    }

    print("\nTOP 5 INTELLIGENCE SCORES")
    print("=" * 100)

    for result in all_scores[:10]:

        if result["candidate_id"] == "CAND_0000021":

            print("\n")
            print("=" * 100)
            print("DEBUG PROJECT MANAGER")
            print("=" * 100)

        candidate = candidate_map[
            result["candidate_id"]
        ]

        for skill in candidate["skills"]:

            print(skill["name"])

        print("=" * 100)

        candidate = candidate_map[
            result["candidate_id"]
        ]

        profile = candidate["profile"]

        print(
            f"\nCandidate ID: "
            f"{candidate['candidate_id']}"
        )

        print(
            f"Title: "
            f"{profile['current_title']}"
        )

        print(
            f"Experience: "
            f"{profile['years_of_experience']} years"
        )

        print(
            f"Company: "
            f"{profile['current_company']}"
        )

        print(
            f"Headline: "
            f"{profile['headline']}"
        )

        print(
            f"Overall Score: "
            f"{result['overall_score']}"
        )

        print(
            f"Career Match: "
            f"{result['career_match_score']}"
        )

        print(
            f"Evidence: "
            f"{result['evidence_score']}"
        )

        print(
            f"Behavior: "
            f"{result['behavior_score']}"
        )

        print(
            f"Trajectory: "
            f"{result['trajectory_score']}"
        )

        print(
            f"Honeypot Risk: "
            f"{result['honeypot_score']}"
        )

        print("-" * 100)