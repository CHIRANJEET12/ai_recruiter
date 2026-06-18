TITLE_LEVELS = {
    "intern": 1,
    "junior": 2,
    "engineer": 3,
    "senior": 4,
    "lead": 5,
    "manager": 6,
    "director": 7,
}


def get_level(title):

    title = title.lower()

    for key, level in TITLE_LEVELS.items():

        if key in title:
            return level

    return 3


def calculate_trajectory_score(candidate):

    history = candidate.get(
        "career_history",
        []
    )

    if len(history) < 2:
        return 50

    levels = [
        get_level(job["title"])
        for job in reversed(history)
    ]

    growth = levels[-1] - levels[0]

    score = 50 + growth * 15

    score = max(
        0,
        min(100, score)
    )

    return score