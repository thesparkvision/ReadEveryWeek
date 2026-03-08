from datetime import datetime

from .. import pipeline
from read_every_week.models import Article


def make_article(url, error=None):
    art = Article(title=url, url=url)
    art.error = error
    art.row_number = 2
    return art


def test_run_skips_errors(monkeypatch, tmp_path):
    # prepare two articles, one has error
    a1 = make_article("u1", error=None)
    a2 = make_article("u2", error="403")
    monkeypatch.setattr(pipeline.sheet, "load_articles", lambda: [a1, a2])

    updates = []
    monkeypatch.setattr(pipeline.sheet, "apply_updates", lambda arts: updates.extend(arts))

    pipeline.run(dry_run=False, retry_errors=False)
    assert updates == [a1]

    updates.clear()
    pipeline.run(dry_run=False, retry_errors=True)
    assert updates == [a1, a2]

