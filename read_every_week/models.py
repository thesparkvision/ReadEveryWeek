from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

def _parse_bool(value):
    if value in (True, "TRUE", "true", "True", 1, "1"):
        return True
    return False

@dataclass
class Article:
    title: str
    url: str
    has_read: bool = False
    worth_revisit: bool = False
    recommended: bool = False
    last_recommended_at: str = ""

    # updated schema: track creator and updater
    created_at: str = ""
    created_by: str = ""
    updated_at: str = ""
    updated_by: str = ""

    reading_time_min: Optional[int] = None

    # inferred metadata
    category: Optional[str] = None

    # diagnostics populated during enrichment
    error: Optional[str] = None
    word_count: Optional[int] = None
    fetched_at: Optional[str] = None
    last_attempted: Optional[str] = None
    recommendation_reason: Optional[str] = None

    row_number: Optional[int] = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, mapping: Dict[str, Any], row_number: int) -> "Article":
        return cls(
            title=mapping.get("title", ""),
            url=mapping.get("url", ""),
            has_read=_parse_bool(mapping.get("has_read")),
            worth_revisit=_parse_bool(mapping.get("worth_revisit", False)),
            recommended=_parse_bool(mapping.get("recommended", False)),
            last_recommended_at=mapping.get("last_recommended_at", ""),
            created_at=mapping.get("created_at", ""),
            created_by=mapping.get("created_by", ""),
            updated_at=mapping.get("updated_at", ""),
            updated_by=mapping.get("updated_by", ""),
            reading_time_min=(mapping.get("reading_time_min")
                               if mapping.get("reading_time_min") not in ("", None)
                               else None),
            error=mapping.get("error") or None,
            word_count=(mapping.get("word_count")
                        if mapping.get("word_count") not in ("", None)
                        else None),
            fetched_at=mapping.get("fetched_at") or None,
            last_attempted=mapping.get("last_attempted") or None,
            category=mapping.get("category") or None,
            row_number=row_number,
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "title": self.title,
            "url": self.url,
            "has_read": self.has_read,
            "worth_revisit": self.worth_revisit,
            "recommended": self.recommended,
            "last_recommended_at": self.last_recommended_at,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
        }
        if self.reading_time_min is not None:
            d["reading_time_min"] = self.reading_time_min
        if self.error is not None:
            d["error"] = self.error
        if self.word_count is not None:
            d["word_count"] = self.word_count
        if self.fetched_at is not None:
            d["fetched_at"] = self.fetched_at
        if self.last_attempted is not None:
            d["last_attempted"] = self.last_attempted
        if self.category is not None:
            d["category"] = self.category
        if self.recommendation_reason is not None:
            d["recommendation_reason"] = self.recommendation_reason
        return d
