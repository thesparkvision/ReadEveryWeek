import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from .. import sheet
from read_every_week.models import Article


class DummyWorksheet:
    def __init__(self):
        self.data = {1: []}  # row number -> list
        self.last_update = None

    def row_values(self, index):
        return self.data.get(index, [])

    def update(self, rng, values):
        # record range and values
        self.last_update = (rng, values)
        # simulate writing header or body
        if rng == "1:1":
            self.data[1] = values[0]
        else:
            # naive placement, ignore
            pass

    def update_cell(self, row, col, val):
        # not used in apply_updates
        raise RuntimeError("should not be called")


def test_apply_updates_batch(monkeypatch):
    w = DummyWorksheet()
    # monkeypatch _get_worksheet to return our dummy
    monkeypatch.setattr(sheet, "_get_worksheet", lambda: w)

    art1 = Article(title="a", url="u1", reading_time_min=5, row_number=2)
    art2 = Article(title="b", url="u2", reading_time_min=10, row_number=3)
    sheet.apply_updates([art1, art2])

    # header should contain required names
    assert "url" in w.data[1]
    assert w.last_update[0].startswith("A2:")
    # values should include both rows
    assert len(w.last_update[1]) == 2


def test_update_article_wrapper(monkeypatch):
    w = DummyWorksheet()
    monkeypatch.setattr(sheet, "_get_worksheet", lambda: w)
    art = Article(title="x", url="y", row_number=5)
    # should not raise
    sheet.update_article(art)
    assert w.last_update is not None
