import json
import pickle

with open("sample_candidates.json","r",encoding="utf-8") as file:
    data = json.load(file)


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

    text += "\nEducation:\n"

    for edu in candidate["education"]:

        text += f"""
Institution: {edu['institution']}
Degree: {edu['degree']}
Field Of Study: {edu['field_of_study']}
Grade: {edu.get('grade', 'N/A')}
Tier: {edu.get('tier', 'unknown')}
"""



    if candidate["certifications"]:

        text += "\nCertifications:\n"

        for cert in candidate["certifications"]:

            text += (
                f"{cert['name']} | "
                f"{cert['issuer']} | "
                f"{cert['year']}\n"
            )


    if candidate["languages"]:

        text += "\nLanguages:\n"

        for lang in candidate["languages"]:

            text += (
                f"{lang['language']} "
                f"({lang['proficiency']})\n"
            )



    text += f"""

Platform Signals

Profile Completeness:
{signals['profile_completeness_score']}

Last Active Date:
{signals['last_active_date']}

Recruiter Response Rate:
{signals['recruiter_response_rate']}

Average Response Time:
{signals['avg_response_time_hours']} hours

Github Activity Score:
{signals['github_activity_score']}

Interview Completion Rate:
{signals['interview_completion_rate']}

Offer Acceptance Rate:
{signals['offer_acceptance_rate']}

Notice Period:
{signals['notice_period_days']} days

Preferred Work Mode:
{signals['preferred_work_mode']}

Willing To Relocate:
{signals['willing_to_relocate']}
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
