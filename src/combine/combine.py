# combine.py

import numpy as np
import pickle
from candidate_builder import all_candidate

JSONL_FILE = "candidates.jsonl"

# =====================================
# LOAD ALL PARTS
# =====================================

print("Loading parts...")

all_embeddings = []
all_ids = []

for part in [1, 2, 3]:

    emb = np.load(f"embeddings_part{part}.npy")
    ids = pickle.load(open(f"ids_part{part}.pkl", "rb"))

    print(f"Part {part}: {emb.shape} | {len(ids):,} ids")

    all_embeddings.append(emb)
    all_ids.extend(ids)

# =====================================
# COMBINE EMBEDDINGS
# =====================================

combined = np.vstack(all_embeddings)

print(f"\nCombined shape: {combined.shape}")
print(f"Total IDs: {len(all_ids):,}")

# =====================================
# BUILD CANDIDATE CORPUS
# =====================================

print("Loading full candidate corpus...")

candidate_corpus = all_candidate(JSONL_FILE)   # ← loads all 100k

print(f"Corpus size: {len(candidate_corpus):,}")

# =====================================
# SAVE ALL
# =====================================

np.save("candidate_embeddings.npy", combined)

pickle.dump(all_ids, open("candidate_ids.pkl", "wb"))

pickle.dump(candidate_corpus, open("candidate_corpus.pkl", "wb"))  # ← added

print("\nDone. Final files:")
print("  candidate_embeddings.npy")
print("  candidate_ids.pkl")
print("  candidate_corpus.pkl")
print("  jd_query_embeddings.npy")