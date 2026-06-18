def calculate_evidence_score(candidate):

    skills = candidate.get(
        "skills",
        []
    )

    if not skills:
        return 0

    endorsement_score = 0
    duration_score = 0

    for skill in skills:

        endorsement_score += min(
            skill.get(
                "endorsements",
                0
            ),
            50
        )

        duration_score += min(
            skill.get(
                "duration_months",
                0
            ),
            60
        )

    endorsement_score /= len(skills)

    duration_score /= len(skills)

    assessments = (
        candidate["redrob_signals"]
        .get(
            "skill_assessment_scores",
            {}
        )
    )

    assessment_score = 0

    if assessments:

        assessment_score = (
            sum(
                assessments.values()
            )
            /
            len(assessments)
        )

    score = (
        endorsement_score * 0.30
        +
        duration_score * 0.30
        +
        assessment_score * 0.40
    )

    return round(
        min(score, 100),
        2
    )