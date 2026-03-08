"""Recommendation rules and helpers.

This module determines which articles should be recommended on a given day
based on configurable "energy" rules.  The rules are defined as a simple map
of weekday name to a dictionary containing ``max_count`` and
``max_total_minutes``.

The default rules match the acceptance criteria from issue #3.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from .models import Article

# rules are kept in a single block so they can be modified easily
DEFAULT_RULES: Dict[str, Dict[str, int]] = {
    "Monday": {"max_count": 1, "max_total_minutes": 15},
    "Thursday": {"max_count": 1, "max_total_minutes": 15},
    "Saturday": {"max_count": 3, "max_total_minutes": 35},
}


def recommend_articles(
    articles: List[Article],
    rules: Optional[Dict[str, Dict[str, int]]] = None,
    date: Optional[datetime] = None,
) -> List[Article]:
    """Return a subset of ``articles`` to recommend on ``date``.

    The algorithm is greedy: it sorts candidates by ascending
    ``reading_time_min`` and picks as many as will fit within the limits
    defined by the rule for that weekday.  If there is no rule for the
    weekday, an empty list is returned.

    ``articles`` that have a ``reading_time_min`` of ``None`` are ignored.

    ``rules`` defaults to :data:`DEFAULT_RULES` but may be supplied to alter
    behaviour (useful for testing or user configuration).
    """
    if rules is None:
        rules = DEFAULT_RULES
    if date is None:
        date = datetime.now()
    weekday = date.strftime("%A")
    rule = rules.get(weekday)
    if not rule:
        return []

    candidates = [a for a in articles if a.reading_time_min is not None]
    candidates.sort(key=lambda a: a.reading_time_min)

    selected: List[Article] = []
    total = 0
    for article in candidates:
        if len(selected) >= rule["max_count"]:
            break
        if total + article.reading_time_min > rule["max_total_minutes"]:
            break
        selected.append(article)
        total += article.reading_time_min
    return selected
