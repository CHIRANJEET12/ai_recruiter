from __future__ import annotations

from typing import Optional

from jd_understanding.parser import JDParserEngine
from jd_understanding.schemas import ParsedJD


class LangChainJDParser:
    def __init__(self, llm: Optional[object] = None):
        self.llm = llm

    def parse(self, raw_jd: str) -> ParsedJD:
        return JDParserEngine.parse(raw_jd)
