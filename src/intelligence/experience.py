def calculate_experience_score(candidate):
    years = candidate["profile"].get(
        "years_of_experience",
        0
    )

    score = min(
        100,
        round(years * 10)
    )

    return score