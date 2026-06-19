from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def resolve_data_dir() -> Path:
    candidates = [ROOT_DIR / "DATA", ROOT_DIR / "data"]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return candidates[0]


def resolve_corpus_path() -> Path:
    return resolve_data_dir() / "candidate_corpus.pkl"
