"""Logic for estimating reading time and related helpers."""

import logging
import math
from datetime import datetime, timezone
from typing import List

from .models import Article
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_READING_WPM = 220
_MIN_READING_MINUTES = 1
_MAX_READING_MINUTES = 180  # clamp to three hours just in case

def fetch_article_html(url: str) -> str:
    """Retrieve the HTML of the page at ``url``."""

    import requests

    headers = {
        "User-Agent": "read-every-week-bot/1.0 (+https://github.com/thesparkvision/ReadEveryWeek)"
    }
    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()
    return response.text


def extract_main_text(html: str) -> str:
    """Extract and return the main article text from ``html``."""

    from bs4 import BeautifulSoup
    from readability import Document

    doc = Document(html)
    summary_html = doc.summary()
    soup = BeautifulSoup(summary_html, "html.parser")
    return soup.get_text(separator=" ")


def calculate_reading_minutes(text: str) -> int:
    """Return a word‑count‑based estimate of reading time in whole minutes."""

    word_count = len(text.split())
    if word_count == 0:
        return _MIN_READING_MINUTES

    minutes = math.ceil(word_count / _READING_WPM)
    minutes = max(_MIN_READING_MINUTES, min(_MAX_READING_MINUTES, minutes))
    return minutes


def classify_url(url: str) -> str:
    """Return a simple category based on the hostname or path.

    Examples: ``medium.com`` -> ``medium``, ``foo.substack.com`` -> ``substack``
    ``reddit.com`` or ``reddit`` -> ``reddit``; ``x.com``/``twitter.com`` -> ``x``.
    Falls back to the bare hostname when nothing matches.
    """
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
    except Exception:
        return ""
    host = host.lower()
    if "medium.com" in host:
        return "medium"
    if "substack.com" in host or host.endswith(".substack.com"):
        return "substack"
    if "reddit.com" in host or "reddit" in host:
        return "reddit"
    if host in ("x.com", "twitter.com"):
        return "x"
    # more rules can be added here
    return host


def enrich_articles(articles: List[Article]) -> None:
    """Fill ``reading_time_min`` on any Article that is missing it.

    The ``Article`` objects are mutated in place; errors and other metadata are
    recorded on the instance so that callers (and the sheet) can see what went
    wrong and avoid retrying permanently broken URLs unless requested.
    """

    logger.info("enriching %d articles", len(articles))
    for article in articles:
        # infer category once at the start
        if article.category is None:
            article.category = classify_url(article.url)

        # record that we attempted this URL regardless of outcome
        article.last_attempted = datetime.now(timezone.utc).isoformat(sep=" ", timespec="seconds")

        if article.reading_time_min not in (None, 0):
            # already have a value, skip
            continue

        logger.info("fetching %s", article.url)
        try:
            html = fetch_article_html(article.url)
            # if title missing, try to pull from HTML <title>
            if not article.title:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(html, "html.parser")
                title_tag = soup.find("title")
                if title_tag and title_tag.string:
                    article.title = title_tag.string.strip()

            text = extract_main_text(html)
            article.word_count = len(text.split())
            article.reading_time_min = calculate_reading_minutes(text)
            article.fetched_at = datetime.now(timezone.utc).isoformat(sep=" ", timespec="seconds")
            logger.info("%s fetched & processed -> %s min", article.url, article.reading_time_min)
        except Exception as exc:  # keep going on failure
            err_msg = str(exc)
            article.error = err_msg
            logger.warning("failed to process %s: %s", article.url, err_msg)
