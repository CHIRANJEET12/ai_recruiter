import json
import pickle

with open(
    "../data/candidate_corpus.pkl",
    "rb",
) as file:
    data = pickle.load(file)


def candidate_to_text(candidate) -> str:

    profile = candidate["profile"]
    signals = candidate["redrob_signals"]

    text = f"""
Candidate Summary

Current Title:
{profile['current_title']}

Years Experience:
{profile['years_of_experience']}

Current Industry:
{profile['current_industry']}

Current Company:
{profile['current_company']}

Location:
{profile['location']}, {profile['country']}

Open To Work:
{signals['open_to_work_flag']}

Github Activity:
{signals['github_activity_score']}

Headline:
{profile['headline']}

Summary:
{profile['summary']}
"""

    text += "\nSkills:\n"

    for skill in candidate["skills"]:
        text += (
            f"{skill['name']} | "
            f"Proficiency: {skill['proficiency']} | "
            f"Endorsements: {skill['endorsements']} | "
            f"Experience: {skill['duration_months']} months\n"
        )

    if signals["skill_assessment_scores"]:

        text += "\nSkill Assessment Scores:\n"

        for skill_name, score in (
            signals["skill_assessment_scores"].items()
        ):
            text += f"{skill_name}: {score}/100\n"

    text += "\nCareer History:\n"

    for job in candidate["career_history"]:

        text += f"""
Title: {job['title']}
Company: {job['company']}
Duration: {job['duration_months']} months
Industry: {job['industry']}
Company Size: {job['company_size']}

Description:
{job['description']}
"""

    return text


def save_candidate(candidate):

    return {
        "candidate_id": candidate["candidate_id"],
        "text": candidate_to_text(candidate),

        "profile": candidate["profile"],
        "skills": candidate["skills"],
        "career_history": candidate["career_history"],
        "education": candidate["education"],
        "certifications": candidate["certifications"],
        "languages": candidate["languages"],
        "redrob_signals": candidate["redrob_signals"]
    }


def all_candidate():

    candidate_corpus = []

    for candidate in data:

        candidate_corpus.append(
            save_candidate(candidate)
        )

    return candidate_corpus


if __name__ == "__main__":

    corpus = all_candidate()

    with open(
        "../data/candidate_corpus.pkl",
        "wb"
    ) as file:

        pickle.dump(
            corpus,
            file
        )

    print(
        f"Saved {len(corpus)} candidates"
    )

    print(
        corpus[0]["candidate_id"]
    )

    print(
        corpus[0].keys()
    )