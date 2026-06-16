from __future__ import annotations

import re
from typing import List, Set, Tuple

from jd_understanding.schemas import ParsedJD
from jd_understanding.terms import (
    PREFERRED_CUES,
    REQUIRED_CUES,
    ROLE_FAMILY_CUES,
    SENIORITY_CUES,
    SKILL_CANONICAL_MAP,
)


class JDParserEngine:
    @staticmethod
    def _normalize_text(text: str) -> str:
        lowered = text.lower()
        lowered = lowered.replace("\n", " ")
        lowered = re.sub(r"\s+", " ", lowered).strip()
        return lowered

    @staticmethod
    def _extract_years_required(text: str) -> int:
        patterns = [
            r"(\d+)\s*\+\s*years",
            r"minimum\s*(\d+)\s*years",
            r"at least\s*(\d+)\s*years",
            r"(\d+)\s*to\s*\d+\s*years",
            r"(\d+)\s*years",
        ]
        extracted: List[int] = []

        for pattern in patterns:
            for match in re.findall(pattern, text):
                extracted.append(int(match))

        return max(extracted) if extracted else 0

    @staticmethod
    def _extract_seniority(text: str) -> str:
        for seniority in ("principal", "staff", "senior", "mid", "junior"):
            cues = SENIORITY_CUES[seniority]
            if any(cue in text for cue in cues):
                return seniority
        return "unknown"

    @staticmethod
    def _extract_role_family(text: str) -> str:
        family_scores = {}
        for family, cues in ROLE_FAMILY_CUES.items():
            family_scores[family] = sum(1 for cue in cues if cue in text)
        best_family = max(family_scores, key=family_scores.get)
        return best_family if family_scores[best_family] > 0 else "general"

    @staticmethod
    def _skill_matches(text: str) -> Set[str]:
        found: Set[str] = set()
        for canonical, aliases in SKILL_CANONICAL_MAP.items():
            if any(alias in text for alias in aliases):
                found.add(canonical)
        return found

    @staticmethod
    def _extract_required_preferred_skills(raw_jd: str) -> Tuple[List[str], List[str]]:
        lines = [line.strip() for line in raw_jd.splitlines() if line.strip()]
        required: Set[str] = set()
        preferred: Set[str] = set()

        for line in lines:
            normalized_line = line.lower()
            matched_skills = JDParserEngine._skill_matches(normalized_line)
            if not matched_skills:
                continue

            if any(cue in normalized_line for cue in REQUIRED_CUES):
                required.update(matched_skills)
            elif any(cue in normalized_line for cue in PREFERRED_CUES):
                preferred.update(matched_skills)
            else:
                required.update(matched_skills)

        preferred -= required
        return sorted(required), sorted(preferred)

    @classmethod
    def parse(cls, raw_jd: str) -> ParsedJD:
        normalized_text = cls._normalize_text(raw_jd)
        required_skills, preferred_skills = cls._extract_required_preferred_skills(raw_jd)

        return ParsedJD(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            seniority=cls._extract_seniority(normalized_text),
            years_required=cls._extract_years_required(normalized_text),
            role_family=cls._extract_role_family(normalized_text),
        )
