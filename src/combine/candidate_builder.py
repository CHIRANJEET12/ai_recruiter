import json


# =====================================
# TEXT BUILDER
# =====================================

def candidate_to_text(candidate):

    profile = candidate.get("profile", {})

    skills = [
        skill["name"]
        for skill in candidate.get("skills", [])
        if skill.get("name")          # skip empty skill names
    ]

    recent_roles = []

    for job in candidate.get("career_history", [])[:3]:

        title = job.get("title", "").strip()
        company = job.get("company", "").strip()

        if title or company:
            recent_roles.append(
                f"{title} at {company}"
            )

    return f"""
Current Title: {profile.get('current_title', '').strip()}

Experience: {profile.get('years_of_experience', 0)} years

Industry: {profile.get('current_industry', '').strip()}

Skills: {', '.join(skills)}

Recent Roles: {' | '.join(recent_roles)}

Headline: {profile.get('headline', '').strip()}

Summary: {profile.get('summary', '').strip()}
""".strip()


# =====================================
# STREAM (memory efficient — one at a time)
# =====================================

def stream_candidates(jsonl_file):

    with open(
        jsonl_file,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:
                candidate = json.loads(line)

                yield {
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

            except (json.JSONDecodeError, KeyError) as e:
                # skip malformed lines instead of crashing
                print(f"Skipping malformed line: {e}")


# =====================================
# CHUNK (for batched processing)
# =====================================

def chunk_candidates(
    jsonl_file,
    chunk_size=5000
):

    chunk = []

    for candidate in stream_candidates(jsonl_file):

        chunk.append(candidate)

        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk


# =====================================
# ALL (loads everything into memory)
# =====================================

def all_candidate(jsonl_file="candidates.jsonl"):
    """
    Returns full list of all candidates.
    Use only when you can afford to load 100k records into RAM.
    For 100k candidates, expect ~500MB–1GB depending on text size.
    """
    return list(stream_candidates(jsonl_file))