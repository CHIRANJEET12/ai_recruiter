# from models.embedding_model import model

def calculate_career_match_score(candidate):

    score = 0

    skills = [
        skill["name"].lower()
        for skill in candidate.get(
            "skills",
            []
        )
    ]

    title = (
        candidate["profile"]
        .get(
            "current_title",
            ""
        )
        .lower()
    )

    # ==================================================
    # Retrieval / Recommendation Skills
    # ==================================================

    skill_weights = {

        "recommendation systems": 30,

        "information retrieval": 25,

        "retrieval": 20,

        "ranking": 20,

        "search": 15,

        "vector search": 20,

        "embeddings": 15,
        "embedding": 15,

        "faiss": 15,
        "pinecone": 15,
        "qdrant": 15,
        "milvus": 15,

        "elasticsearch": 10,
        "opensearch": 10,
        "bm25": 10,

        "machine learning": 10,
        "nlp": 10,

        "python": 5,

        "llm": 3,
        "fine-tuning llms": 3,
        "lora": 3,
        "peft": 3,

        "langchain": 3,
        "mlflow": 3,
        "bentoml": 3
    }

    # ==================================================
    # Skill Score
    # ==================================================

    skill_score = 0

    for skill in skills:

        for target, weight in skill_weights.items():

            if target in skill:
                skill_score += weight

    score += min(
        skill_score,
        60
    )

    # ==================================================
    # Career History
    # ==================================================

    history_text = ""

    for job in candidate.get(
        "career_history",
        []
    ):

        history_text += " "

        history_text += job.get(
            "description",
            ""
        ).lower()

    production_terms = [

        "recommendation",

        "retrieval",

        "ranking",

        "search",

        "vector search",

        "candidate generation",

        "relevance",

        "embeddings",

        "faiss",

        "pinecone",

        "qdrant",

        "milvus",

        "elasticsearch",

        "opensearch",

        "a/b testing",

        "evaluation",

        "production",

        "deployed",

        "deployment"
    ]

    history_score = 0

    for term in production_terms:

        if term in history_text:
            history_score += 5

    score += min(
        history_score,
        25
    )

    # ==================================================
    # Title Boosts
    # ==================================================

    if "recommendation" in title:
        score += 35

    elif "retrieval" in title:
        score += 30

    elif "search" in title:
        score += 30

    elif "ranking" in title:
        score += 30

    elif "machine learning engineer" in title:
        score += 20

    elif "ml engineer" in title:
        score += 20

    elif "ai engineer" in title:
        score += 15

    elif "backend engineer" in title:
        score += 10

    elif "data engineer" in title:
        score += 8

    elif "data scientist" in title:
        score += 8

    # ==================================================
    # Hard Caps
    # ==================================================

    if "project manager" in title:
        return 30

    if "marketing" in title:
        return 20

    if "sales" in title:
        return 20

    if "hr" in title:
        return 15

    if "frontend" in title:
        return min(score, 40)

    if "ui" in title:
        return min(score, 40)

    if "qa" in title:
        return min(score, 35)

    if "cloud engineer" in title:
        return min(score, 55)

    if "devops" in title:
        return min(score, 55)

    if ".net" in title:
        return min(score, 45)

    if "full stack" in title:
        return min(score, 45)

    # ==================================================
    # Final Score
    # ==================================================

    score = max(
        0,
        min(score, 100)
    )

    return round(score)