def calculate_behavior_score(candidate):

    signals = candidate["redrob_signals"]

    response_rate = min(
        max(
            signals.get(
                "recruiter_response_rate",
                0
            ),
            0
        ),
        1
    ) * 100

    interview_rate = min(
        max(
            signals.get(
                "interview_completion_rate",
                0
            ),
            0
        ),
        1
    ) * 100

    offer_rate = min(
        max(
            signals.get(
                "offer_acceptance_rate",
                0
            ),
            0
        ),
        1
    ) * 100

    github_score = min(
        max(
            signals.get(
                "github_activity_score",
                0
            ),
            0
        ),
        10
    ) * 10

    profile_score = min(
        max(
            signals.get(
                "profile_completeness_score",
                0
            ),
            0
        ),
        100
    )

    score = (
        response_rate * 0.30
        +
        interview_rate * 0.25
        +
        offer_rate * 0.15
        +
        github_score * 0.15
        +
        profile_score * 0.15
    )

    return round(
        min(score, 100),
        2
    )