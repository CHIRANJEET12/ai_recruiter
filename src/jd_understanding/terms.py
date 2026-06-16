SKILL_CANONICAL_MAP = {
    "python": ["python"],
    "information retrieval": ["information retrieval", "retrieval", "ir"],
    "ranking": ["ranking", "reranking", "re-ranking", "learning to rank", "ltr"],
    "semantic search": ["semantic search", "vector search", "dense retrieval"],
    "hybrid search": ["hybrid search"],
    "embeddings": ["embedding", "embeddings", "sentence transformers", "transformer embeddings"],
    "vector databases": ["vector database", "vector db", "vector databases", "vectordb"],
    "pinecone": ["pinecone"],
    "milvus": ["milvus"],
    "qdrant": ["qdrant"],
    "faiss": ["faiss"],
    "nlp": ["nlp", "natural language processing"],
    "production ml systems": ["production ml", "production ml systems", "production machine learning"],
    "a/b testing": ["a/b testing", "ab testing", "online experimentation"],
    "offline evaluation": ["offline evaluation", "ndcg", "mrr", "map"],
}

REQUIRED_CUES = {
    "must",
    "need",
    "required",
    "mandatory",
    "requirement",
    "you should have",
}

PREFERRED_CUES = {
    "preferred",
    "nice to have",
    "plus",
    "good to have",
    "bonus",
}

ROLE_FAMILY_CUES = {
    "search": ["search", "retrieval", "ranking", "matching", "recommendation"],
    "ml_platform": ["ml platform", "mlops", "feature store", "model serving"],
    "backend_ai": ["backend", "api", "distributed systems", "infra"],
}

SENIORITY_CUES = {
    "principal": ["principal", "architect", "lead architect", "director"],
    "staff": ["staff", "tech lead", "lead engineer"],
    "senior": ["senior", "sr", "sde 3", "level 5"],
    "mid": ["mid", "intermediate", "sde 2", "level 3", "level 4"],
    "junior": ["junior", "jr", "entry", "associate", "sde 1", "fresher"],
}
