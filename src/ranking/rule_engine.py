from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List


class RuleBasedReranker:
    def rerank(
        self,
        candidates: List[Dict[str, Any]],
        top_k: int = 100,
    ) -> List[Dict[str, Any]]:
        scored = []
        for candidate in candidates:
            cross = float(candidate.get("cross_score", 0.0))
            availability_bump = self._availability_bump(candidate)
            availability_penalty = self._availability_penalty(candidate)
            composite = cross + availability_bump - availability_penalty
            payload = dict(candidate)
            payload["stage3_score"] = round(composite, 6)
            payload["availability_bump"] = round(availability_bump, 4)
            payload["availability_penalty"] = round(availability_penalty, 4)
            scored.append(payload)

        scored.sort(key=lambda x: x["stage3_score"], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _availability_bump(candidate: Dict[str, Any]) -> float:
        bump = 0.0
        signals = candidate.get("redrob_signals", {})

        if signals.get("open_to_work_flag", False):
            bump += 0.08

        if signals.get("willing_to_relocate", False):
            bump += 0.04

        response_rate = signals.get("recruiter_response_rate", 0)
        if isinstance(response_rate, (int, float)) and response_rate > 0.5:
            bump += 0.03

        return bump

    @staticmethod
    def _availability_penalty(candidate: Dict[str, Any]) -> float:
        penalty = 0.0
        signals = candidate.get("redrob_signals", {})

        notice_days = signals.get("notice_period_days", 0)
        if isinstance(notice_days, (int, float)) and notice_days > 60:
            penalty += 0.06
        elif isinstance(notice_days, (int, float)) and notice_days > 30:
            penalty += 0.03

        last_active = signals.get("last_active_date", None)
        if last_active:
            try:
                if isinstance(last_active, str):
                    active_date = datetime.fromisoformat(last_active)
                else:
                    active_date = last_active
                now = datetime.now(timezone.utc)
                if active_date.tzinfo is None:
                    active_date = active_date.replace(tzinfo=timezone.utc)
                days_since = (now - active_date).days
                if days_since > 180:
                    penalty += 0.05
                elif days_since > 90:
                    penalty += 0.02
            except (ValueError, TypeError):
                pass

        return penalty
