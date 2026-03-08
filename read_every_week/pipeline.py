"""Main pipeline for loading articles, enriching metadata, and generating recommendations."""

import logging
import os
from datetime import datetime, timezone
from typing import List

from read_every_week.emailer import send_recommendation_email

from . import reading_time, sheet
from .models import Article
from .recommendation.engine import recommend_articles

logger = logging.getLogger(__name__)


def run(dry_run: bool = False, retry_errors: bool = False) -> int:
    logger.info("starting pipeline (dry_run=%s, retry_errors=%s)", dry_run, retry_errors)

    articles: List[Article] = sheet.load_articles()
    logger.info("loaded %d articles from sheet", len(articles))

    if not articles:
        logger.info("no articles to process")
        return 0

    if not retry_errors:
        original_count = len(articles)
        articles = [article for article in articles if not article.error]
        logger.info(
            "skipping %d errored articles, %d remaining",
            original_count - len(articles),
            len(articles),
        )

    reading_time.enrich_articles(articles)

    primary_articles, worth_revisit_articles = recommend_articles(articles)

    logger.info("primary recommendations:")
    for article in primary_articles:
        logger.info("  %s (%s min)", article.title, article.reading_time_min)

    logger.info("worth revisit suggestions:")
    for article in worth_revisit_articles:
        logger.info("  %s (%s min)", article.title, article.reading_time_min)

    if not primary_articles:
        logger.info("no recommendations; skipping email")
        return 0

    logger.info("sending recommendation email")

    email_sent = send_recommendation_email(primary_articles, worth_revisit_articles)

    if not email_sent:
        logger.error("email failed; aborting update")
        return 1

    now = datetime.now(timezone.utc).isoformat(sep=" ", timespec="seconds")
    updated_by = os.environ.get("UPDATED_BY", "script")

    for article in articles:
        article.updated_at = now
        article.updated_by = updated_by

    for article in primary_articles:
        article.recommended = True
        article.last_recommended_at = now

        article.recommendation_reason = "primary_selection"

    for article in worth_revisit_articles:
        article.recommendation_reason = "worth_revisit"

    if dry_run:
        logger.info("dry run; would update %d rows", len(articles))
    else:
        sheet.apply_updates(articles)
        logger.info("wrote %d rows", len(articles))

    logger.info("pipeline complete")
    return 0
