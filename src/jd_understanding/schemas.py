from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


VALID_SENIORITY = {"junior", "mid", "senior", "staff", "principal", "unknown"}


@dataclass(frozen=True)
class ParsedJD:
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    seniority: str = "unknown"
    years_required: int = 0
    role_family: str = "general"

    def __post_init__(self) -> None:
        normalized_seniority = self.seniority.lower().strip()
        if normalized_seniority not in VALID_SENIORITY:
            raise ValueError(
                f"Invalid seniority '{self.seniority}'. "
                f"Expected one of: {sorted(VALID_SENIORITY)}"
            )

        object.__setattr__(
            self,
            "required_skills",
            sorted({skill.strip().lower() for skill in self.required_skills if skill.strip()}),
        )
        object.__setattr__(
            self,
            "preferred_skills",
            sorted({skill.strip().lower() for skill in self.preferred_skills if skill.strip()}),
        )
        object.__setattr__(self, "seniority", normalized_seniority)
        object.__setattr__(self, "years_required", max(0, int(self.years_required)))
        object.__setattr__(self, "role_family", self.role_family.strip().lower() or "general")

    def to_dict(self) -> Dict[str, object]:
        return {
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "seniority": self.seniority,
            "years_required": self.years_required,
            "role_family": self.role_family,
        }


@dataclass(frozen=True)
class ScoreWeights:
    cross: float
    experience: float
    behavior: float
    evidence: float
    trajectory: float

    def __post_init__(self) -> None:
        weights = {
            "cross": float(self.cross),
            "experience": float(self.experience),
            "behavior": float(self.behavior),
            "evidence": float(self.evidence),
            "trajectory": float(self.trajectory),
        }

        if any(value < 0 for value in weights.values()):
            raise ValueError("Weights must be non-negative")

        total = sum(weights.values())
        if total <= 0:
            raise ValueError("At least one weight must be greater than zero")

        normalized = {key: value / total for key, value in weights.items()}
        object.__setattr__(self, "cross", normalized["cross"])
        object.__setattr__(self, "experience", normalized["experience"])
        object.__setattr__(self, "behavior", normalized["behavior"])
        object.__setattr__(self, "evidence", normalized["evidence"])
        object.__setattr__(self, "trajectory", normalized["trajectory"])

    def to_dict(self) -> Dict[str, float]:
        return {
            "cross": self.cross,
            "experience": self.experience,
            "behavior": self.behavior,
            "evidence": self.evidence,
            "trajectory": self.trajectory,
        }
