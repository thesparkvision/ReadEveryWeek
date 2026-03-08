from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from ..models import Article


def is_article_eligible(
    article: Article,
    cutoff_timestamp: Optional[float],
) -> bool:
    if article.reading_time_min is None:
        return False

    if article.has_read:
        return False

    if cutoff_timestamp is None:
        return True

    if not article.last_recommended_at:
        return True

    try:
        last_recommended_timestamp = datetime.fromisoformat(
            article.last_recommended_at
        ).timestamp()
    except Exception:
        return True

    return last_recommended_timestamp <= cutoff_timestamp


def filter_eligible_articles(
    articles: List[Article],
    cooldown_days: Optional[int],
    current_time: datetime,
) -> List[Article]:

    cutoff_timestamp: Optional[float] = None

    if cooldown_days:
        cutoff_timestamp = current_time.timestamp() - cooldown_days * 86400

    return [
        article
        for article in articles
        if is_article_eligible(article, cutoff_timestamp)
    ]


def split_worth_revisit_articles(
    articles: List[Article],
) -> tuple[List[Article], List[Article]]:

    regular_articles: List[Article] = []
    worth_revisit_articles: List[Article] = []

    for article in articles:
        if article.worth_revisit:
            worth_revisit_articles.append(article)
        else:
            regular_articles.append(article)

    return regular_articles, worth_revisit_articles