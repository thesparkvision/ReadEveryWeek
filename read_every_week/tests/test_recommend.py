import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from datetime import datetime
from typing import Optional

from read_every_week import recommend
from read_every_week.models import Article


def make_article(time: Optional[int]) -> Article:
    art = Article(title="x", url="u")
    art.reading_time_min = time
    return art


def test_recommend_day_rules():
    arts = [make_article(t) for t in (5, 10, 20, 30)]
    # Monday should pick one <=15, so the 5-minute item
    monday = datetime(2026, 3, 9)  # Monday
    rec = recommend.recommend_articles(arts, date=monday)
    assert len(rec) == 1
    assert rec[0].reading_time_min == 5

    # Thursday same
    thurs = datetime(2026, 3, 12)
    rec = recommend.recommend_articles(arts, date=thurs)
    assert len(rec) == 1
    assert rec[0].reading_time_min == 5

    # Saturday picks 3 items total <=35: 5+10+20=35
    sat = datetime(2026, 3, 14)
    rec = recommend.recommend_articles(arts, date=sat)
    assert len(rec) == 3
    assert sum(a.reading_time_min for a in rec) <= 35

    # Sunday or other day returns empty
    sun = datetime(2026, 3, 15)
    assert recommend.recommend_articles(arts, date=sun) == []


def test_custom_rules_override():
    arts = [make_article(t) for t in (5, 10, 20)]
    rules = {"Wednesday": {"max_count": 2, "max_total_minutes": 100}}
    wed = datetime(2026, 3, 11)
    rec = recommend.recommend_articles(arts, rules=rules, date=wed)
    assert len(rec) == 2
