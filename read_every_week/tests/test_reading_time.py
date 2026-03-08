from datetime import datetime, timezone

import pytest

from .. import reading_time
from ..models import Article


def test_enrich_success(monkeypatch):
    sample_html = "<html><head><title>My title</title></head><body><p>Hello world</p></body></html>"

    monkeypatch.setattr(reading_time, "fetch_article_html", lambda url: sample_html)
    monkeypatch.setattr(reading_time, "extract_main_text", lambda html: "Hello world")

    art = Article(title="", url="https://medium.com/foo/bar")
    reading_time.enrich_articles([art])
    assert art.reading_time_min == 1  # one word -> clamp to min
    assert art.error is None
    assert art.word_count == 2 - 1 + 1  # simplified but positive
    assert art.fetched_at is not None
    assert art.last_attempted is not None
    # title should be filled from HTML
    assert art.title == "My title"
    # category inferred
    assert art.category == "medium"


def test_enrich_failure(monkeypatch):
    def fail(url):
        raise RuntimeError("boom")

    monkeypatch.setattr(reading_time, "fetch_article_html", fail)

    art = Article(title="t", url="u")
    reading_time.enrich_articles([art])
    assert art.reading_time_min is None
    assert art.error == "boom"
    assert art.last_attempted is not None


def test_classify_url():
    assert reading_time.classify_url("https://medium.com/foo") == "medium"
    assert reading_time.classify_url("https://some.substack.com/post") == "substack"
    assert reading_time.classify_url("https://reddit.com/r/python") == "reddit"
    assert reading_time.classify_url("https://x.com/xyz") == "x"
    # fallback to hostname
    assert reading_time.classify_url("https://example.org/page") == "example.org"
