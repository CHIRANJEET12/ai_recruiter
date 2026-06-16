import pickle

class CandidateRepository:

    def __init__(self, path):
        self.path = path
        raw_data = self.loadCandidates()

        self.candidates = {c["candidate_id"]: c for c in raw_data}
    
    def loadCandidates(self):
        print("\nLoading Candidate Corpus...\n")

        with open(self.path, "rb") as f:
            return pickle.load(f)
        
    def getCandidates(self, candidate_id):
        return self.candidates[candidate_id]