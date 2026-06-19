from common.paths import resolve_corpus_path, resolve_data_dir
from intelligence.main import Intelligence


def test_data_dir_resolution_works_with_uppercase_data_folder():
    data_dir = resolve_data_dir()
    assert data_dir.name.lower() == "data"


def test_corpus_path_resolution_points_to_candidate_corpus_file():
    corpus_path = resolve_corpus_path()
    assert corpus_path.name == "candidate_corpus.pkl"


def test_intelligence_uses_default_resolved_corpus_path_without_crashing():
    intelligence = Intelligence()
    assert intelligence.respository.getallCandidates()
