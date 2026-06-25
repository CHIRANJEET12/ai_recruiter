import faiss
import pickle
import numpy as np

index = faiss.read_index(
    "candidate_faiss.index"
)

with open(
    "candidate_ids.pkl",
    "rb"
) as f:
    candidate_ids = pickle.load(f)

jd_embedding = np.load(
    "jd_embedding.npy"
)

scores, indices = index.search(
    jd_embedding.reshape(1, -1),
    k=20
)

for rank, (score, idx) in enumerate(
    zip(
        scores[0],
        indices[0]
    ),
    start=1
):

    print(
        f"{rank}. "
        f"{candidate_ids[idx]}"
        f" | score={score:.4f}"
    )