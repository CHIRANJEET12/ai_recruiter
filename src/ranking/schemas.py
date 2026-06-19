from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class CandidateComponentScores:
    candidate_id: str
    cross_score: Optional[float] = None
    experience_score: Optional[float] = None
    behavior_score: Optional[float] = None
    evidence_score: Optional[float] = None
    trajectory_score: Optional[float] = None

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "cross": self.cross_score,
            "experience": self.experience_score,
            "behavior": self.behavior_score,
            "evidence": self.evidence_score,
            "trajectory": self.trajectory_score,
        }


@dataclass
class RankedCandidate:
    candidate_id: str
    final_score: float
    score_breakdown: Dict[str, float]
    reasoning: str
