import logging
import os
from datetime import datetime, timezone
from typing import List

from . import reading_time, sheet
from .models import Article

logger = logging.getLogger(__name__)


def run(dry_run: bool = False, retry_errors: bool = False) -> int:
    logger.info("starting pipeline (dry_run=%s, retry_errors=%s)\n", dry_run, retry_errors)
    articles: List[Article] = sheet.load_articles()
    logger.info("loaded %d articles from sheet\n", len(articles))
    if not articles:
        logger.info("no articles to process\n")
        return 0

    if not retry_errors:
        # skip rows that already failed once
        original = len(articles)
        articles = [a for a in articles if not a.error]
        logger.info("skipping %d errored articles, %d remaining\n", original - len(articles), len(articles))

    reading_time.enrich_articles(articles)

    now = datetime.now(timezone.utc).isoformat(sep=' ', timespec='seconds')
    for art in articles:
        art.updated_at = now
        art.updated_by = os.environ.get("UPDATED_BY", "script")

    if dry_run:
        logger.info("dry run; would update %d rows\n", len(articles))
    else:
        sheet.apply_updates(articles)
        logger.info("wrote %d rows\n", len(articles))

    logger.info("pipeline complete\n")
    return 0
