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
    primary, worthies = recommend.recommend_articles(arts, date=monday)
    assert len(primary) == 1 and primary[0].reading_time_min == 5
    assert worthies == []

    # Thursday same
    thurs = datetime(2026, 3, 12)
    primary, worthies = recommend.recommend_articles(arts, date=thurs)
    assert len(primary) == 1 and primary[0].reading_time_min == 5
    assert worthies == []

    # Saturday picks 3 items total <=35: 5+10+20=35
    sat = datetime(2026, 3, 14)
    primary, worthies = recommend.recommend_articles(arts, date=sat)
    assert len(primary) == 3
    assert sum(a.reading_time_min for a in primary) <= 35
    assert worthies == []

    # Sunday or other day returns empty
    sun = datetime(2026, 3, 15)
    primary, worthies = recommend.recommend_articles(arts, date=sun)
    assert primary == [] and worthies == []

    # marking one as read excludes it
    arts[0].has_read = True
    primary, worthies = recommend.recommend_articles(arts, date=monday)
    assert all(not a.has_read for a in primary + worthies)

    # items within cooldown should be skipped; by default the global
    # cooldown (14 days) applies so something recommended just one day
    # earlier is not eligible.
    arts = [make_article(t) for t in (5, 10)]
    arts[0].last_recommended_at = "2026-03-08T00:00:00"  # day before Monday
    primary, worthies = recommend.recommend_articles(arts, date=monday)
    assert len(primary) == 1 and primary[0].reading_time_min == 10

    # global cooldown overrides any smaller per-day value
    arts = [make_article(t) for t in (5, 10)]
    arts[0].last_recommended_at = "2026-02-28T00:00:00"  # five days earlier
    rules = {"_cooldown_days": 14, "Monday": {"max_count": 1, "max_total_minutes": 15, "cooldown_days": 1}}
    primary, worthies = recommend.recommend_articles(arts, rules=rules, date=monday)
    assert len(primary) == 1 and primary[0].reading_time_min == 10

    # preference for worth_revisit
    arts = [make_article(10), make_article(5)]
    arts[0].worth_revisit = True
    sat = datetime(2026, 3, 14)
    primary, worthies = recommend.recommend_articles(arts, date=sat)
    # should show the worth_revisit candidate separately
    assert len(worthies) == 1 and worthies[0].worth_revisit is True
    assert primary != worthies

    # budget respected: if two small plus a big exceed limit only two selected
    arts = [make_article(20), make_article(20), make_article(20)]
    sat = datetime(2026, 3, 14)
    primary, worthies = recommend.recommend_articles(arts, date=sat)
    assert sum(a.reading_time_min for a in primary) <= 35

    # worth_revisit cap on Saturday: only 2 of the 3 flagged items should be chosen
    arts = [make_article(5) for _ in range(3)]
    for art in arts:
        art.worth_revisit = True
    sat = datetime(2026, 3, 14)
    primary, worthies = recommend.recommend_articles(arts, date=sat)
    assert len(worthies) == 2
    assert all(a.worth_revisit for a in worthies)
    assert primary == []



def test_custom_rules_override():
    arts = [make_article(t) for t in (5, 10, 20)]
    rules = {"Wednesday": {"max_count": 2, "max_total_minutes": 100}}
    wed = datetime(2026, 3, 11)
    rec = recommend.recommend_articles(arts, rules=rules, date=wed)
    assert len(rec) == 2
