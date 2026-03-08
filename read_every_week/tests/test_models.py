import sys, os

# ensure package root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from datetime import datetime

from ..models import Article


def test_article_roundtrip():
    # create an article with all optional fields
    now = datetime.now().isoformat()
    art = Article(
        title="foo",
        url="https://example.com",
        created_at=now,
        created_by="me",
        updated_at=now,
        updated_by="me",
        reading_time_min=5,
        error="oops",
        word_count=250,
        fetched_at=now,
        last_attempted=now,
    )

    d = art.to_dict()
    assert d["title"] == "foo"
    assert d["url"] == "https://example.com"
    assert d["reading_time_min"] == 5
    assert d["error"] == "oops"
    assert d["word_count"] == 250
    assert d["fetched_at"] == now
    assert d["last_attempted"] == now

    # round‑trip via from_dict
    art2 = Article.from_dict(d, row_number=7)
    assert art2.title == art.title
    assert art2.error == art.error
    assert art2.row_number == 7
