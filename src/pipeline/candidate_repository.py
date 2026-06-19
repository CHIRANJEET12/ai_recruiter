import pickle
import json
from pathlib import Path

class CandidateRepository:

    def __init__(self, path):
        self.path = path
        raw_data = self.loadCandidates()

        self.candidates = {c["candidate_id"]: c for c in raw_data}
        self.candidate_details = self._load_candidate_details()

    def _load_candidate_details(self):
        corpus_path = Path(self.path)
        parent = corpus_path.parent
        detail_candidates = [
            parent / "sample_candidates.json",
            parent.parent / "sample_candidates.json",
            Path("sample_candidates.json"),
        ]

        for candidate_path in detail_candidates:
            if not candidate_path.exists():
                continue
            with open(candidate_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return {c["candidate_id"]: c for c in data if "candidate_id" in c}
        return {}
    
    def loadCandidates(self):
        print("\nLoading Candidate Corpus...\n")

        with open(self.path, "rb") as f:
            return pickle.load(f)
        
    def getallCandidates(self):
        return self.candidates

    def getallEnrichedCandidates(self):
        if not self.candidate_details:
            return self.candidates

        enriched = {}
        for candidate_id, corpus_record in self.candidates.items():
            detail_record = self.candidate_details.get(candidate_id, {})
            enriched[candidate_id] = {**detail_record, **corpus_record}
        return enriched
        
    def getCandidates(self, candidate_id):
        return self.candidates[candidate_id]

    def getEnrichedCandidate(self, candidate_id):
        corpus_record = self.candidates.get(candidate_id, {})
        detail_record = self.candidate_details.get(candidate_id, {})
        return {**detail_record, **corpus_record}
