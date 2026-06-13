from candidate_builder import all_candidate
from sentence_transformers import SentenceTransformer

import pickle
import numpy as np

print("Loading candidates...")

candidate_corpus = all_candidate()

documents = [
    c["text"]
    for c in candidate_corpus
]

candidate_ids = [
    c["candidate_id"]
    for c in candidate_corpus
]

print("Loading model...")

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

print("Creating embeddings...")

embeddings = model.encode(
    documents,
    normalize_embeddings=True,
    show_progress_bar=True
)

pickle.dump(
    candidate_corpus,
    open("candidate_corpus.pkl", "wb")
)

pickle.dump(
    candidate_ids,
    open("candidate_ids.pkl", "wb")
)

np.save(
    "candidate_embeddings.npy",
    embeddings
)

print("Index saved.")