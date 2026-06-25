# build_index_part.py
# =====================================
# CHANGE ONLY THESE 3 LINES
# =====================================


PART = 1          # 1, 2, or 3
START = 0         # Part1: 0 | Part2: 34000 | Part3: 67000
END = 34000       # Part1: 34000 | Part2: 67000 | Part3: 100000

# =====================================
# CONFIG (same for everyone)
# =====================================

JSONL_FILE = "candidates.jsonl"
BATCH_SIZE = 256
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# =====================================
# IMPORTS
# =====================================

from combine.candidate_builder import stream_candidates
from sentence_transformers import SentenceTransformer
from pipeline.timmer import Timer
from jd_Parser.jd_parser import JDParser
import numpy as np
import pickle
import time

# =====================================
# JD EMBEDDING (only Part 1 does this)
# =====================================

print("Loading model...")

model = SentenceTransformer(MODEL_NAME)

if PART == 1:

    print("Creating JD embedding...")

    jd_query = JDParser.get_jd()

    jd_embedding = model.encode(
        jd_query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)

    np.save("jd_query_embeddings.npy", jd_embedding)

    print(f"JD Embedding shape: {jd_embedding.shape}")
    print("Saved → jd_query_embeddings.npy")

# =====================================
# LOAD SLICE
# =====================================

print(f"\nPart {PART} | Candidates {START:,} → {END:,}")
print("Loading candidates...")

all_docs = []
all_ids = []

for i, candidate in enumerate(stream_candidates(JSONL_FILE)):
    if i < START:
        continue
    if i >= END:
        break
    all_docs.append(candidate["text"])
    all_ids.append(candidate["candidate_id"])

print(f"Loaded: {len(all_docs):,} candidates")

# =====================================
# ENCODE
# =====================================

print(f"Encoding | batch_size={BATCH_SIZE}...")

timer = Timer()
timer.start()

embeddings = model.encode(
    all_docs,
    batch_size=BATCH_SIZE,
    normalize_embeddings=True,
    show_progress_bar=True,
    convert_to_numpy=True,
).astype(np.float32)

duration = timer.end()

print(f"Done in {duration/60:.1f} min")
print(f"Shape: {embeddings.shape}")

# =====================================
# SAVE
# =====================================

np.save(f"embeddings_part{PART}.npy", embeddings)
pickle.dump(all_ids, open(f"ids_part{PART}.pkl", "wb"))

print(f"Saved → embeddings_part{PART}.npy + ids_part{PART}.pkl")