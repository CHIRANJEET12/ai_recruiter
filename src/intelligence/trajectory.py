TITLE_LEVELS = {

    "intern": 1,

    "associate": 2,
    "junior": 2,

    "engineer": 3,
    "developer": 3,
    "analyst": 3,

    "senior": 4,

    "staff": 5,
    "lead": 5,

    "principal": 6,
    "architect": 6,

    "manager": 7,

    "director": 8,

    "vp": 9,
    "vice president": 9,

    "head": 10
}


def get_level(title):

    title = title.lower()

    matched_level = 3

    for keyword, level in TITLE_LEVELS.items():

        if keyword in title:

            matched_level = max(
                matched_level,
                level
            )

    return matched_level


def calculate_trajectory_score(candidate):

    history = candidate.get(
        "career_history",
        []
    )

    # Not enough history
    if len(history) < 2:

        return 50

    levels = [

        get_level(
            job.get(
                "title",
                ""
            )
        )

        for job in reversed(history)
    ]

    total_growth = 0

    promotion_count = 0

    demotion_count = 0

    for i in range(
        1,
        len(levels)
    ):

        change = (
            levels[i]
            -
            levels[i - 1]
        )

        total_growth += change

        if change > 0:

            promotion_count += 1

        elif change < 0:

            demotion_count += 1

    score = 50

    # Overall growth
    score += total_growth * 12

    # Reward consistent promotions
    score += promotion_count * 5

    # Penalize demotions
    score -= demotion_count * 5

    # Cap score
    score = max(
        0,
        min(
            score,
            100
        )
    )

    return round(score)