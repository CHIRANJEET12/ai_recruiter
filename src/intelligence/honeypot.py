from .evidence import calculate_evidence_score


def calculate_honeypot_score(candidate):

    risk = 0

    skills = candidate.get(
        "skills",
        []
    )

    years = (
        candidate["profile"]
        .get(
            "years_of_experience",
            0
        )
    )

    evidence_score = (
        calculate_evidence_score(
            candidate
        )
    )

    if evidence_score < 25:
        risk += 20

    advanced_skills = len([
        s
        for s in skills
        if s.get(
            "proficiency",
            ""
        ).lower() in [
            "advanced",
            "expert"
        ]
    ])

    if len(skills) > years * 2:
        risk += 15

    if advanced_skills > 10:
        risk += 10

    title = (
        candidate["profile"]
        .get(
            "current_title",
            ""
        )
        .lower()
    )

    if "marketing" in title:
        risk += 40

    if "project manager" in title:
        risk += 35

    history_text = ""

    for job in candidate.get(
        "career_history",
        []
    ):

        history_text += (
            " "
            + job.get(
                "company",
                ""
            )
            + " "
            + job.get(
                "title",
                ""
            )
        ).lower()

    consulting_companies = [
        "infosys",
        "tcs",
        "wipro",
        "cognizant",
        "accenture",
        "capgemini"
    ]

    consulting_count = 0

    for company in consulting_companies:

        if company in history_text:
            consulting_count += 1

    if consulting_count >= 2:
        risk += 20

    skill_names = " ".join([
        s["name"].lower()
        for s in skills
    ])

    if (
        "langchain" in skill_names
        and
        years > 8
    ):
        risk += 15

    return min(
        risk,
        100
    )