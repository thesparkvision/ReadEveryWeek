from __future__ import annotations
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..models import Article
from .candidate_generation import (
    filter_eligible_articles,
    split_worth_revisit_articles,
)
from .strategies import STRATEGIES
logger = logging.getLogger(__name__)

DEFAULT_RULES: Dict[str, Dict[str, int]] = {
    "_cooldown_days": 14,
    "Monday": {"max_count": 1, "max_total_minutes": 15},
    "Thursday": {"max_count": 1, "max_total_minutes": 15},
    "Saturday": {
        "max_count": 3,
        "max_total_minutes": 35,
        "max_worth_revisit": 2,
    },
}


def recommend_articles(
    articles: List[Article],
    rules: Optional[Dict[str, Dict[str, int]]] = None,
    date: Optional[datetime] = None,
    strategy: str = "stochastic_sampling",
) -> Tuple[List[Article], List[Article]]:
    """Return recommended articles for the given day.

    The recommendation process follows a simple pipeline:

    1. Determine today's rule configuration.
    2. Filter eligible articles (cooldown, unread, valid reading time).
    3. Separate worth-revisit articles from regular candidates.
    4. Select primary recommendations using the chosen strategy.

    Returns:
        primary_articles: main recommendations
        worth_revisit_articles: additional optional revisit picks
    """

    if rules is None:
        rules = DEFAULT_RULES

    if date is None:
        date = datetime.now()

    weekday = date.strftime("%A")
    rule = rules.get(weekday)

    if not rule:
        return [], []

    cooldown_days = rules.get("_cooldown_days", rule.get("cooldown_days"))

    eligible_articles = filter_eligible_articles(
        articles,
        cooldown_days,
        date,
    )

    regular_articles, worth_revisit_articles = split_worth_revisit_articles(
        eligible_articles
    )

    worth_revisit_articles.sort(
        key=lambda article: article.reading_time_min
    )

    max_worth_revisit = rule.get("max_worth_revisit", 0)

    worth_revisit_selection = worth_revisit_articles[:max_worth_revisit]

    remaining_worth_revisit = worth_revisit_articles[max_worth_revisit:]

    candidate_articles = regular_articles + remaining_worth_revisit

    logger.info("total articles: %d", len(articles))
    logger.info("eligible articles: %d", len(eligible_articles))
    logger.info("regular articles: %d", len(regular_articles))
    logger.info("worth revisit articles: %d", len(worth_revisit_articles))
    logger.info("candidate articles: %d", len(candidate_articles))

    strategy_instance = STRATEGIES.get(strategy, STRATEGIES["greedy"])

    primary_selection = strategy_instance.select(
        candidate_articles,
        rule,
    )

    return primary_selection, worth_revisit_selection
