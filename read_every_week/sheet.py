"""Utilities for interacting with the Google Sheet that stores articles."""

from typing import List

import gspread
from google.auth import default

from .models import Article


def _authenticate() -> gspread.Client:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)


def _get_worksheet():
    client = _authenticate()
    try:
        spreadsheet = client.open_by_key(__import__("os").environ["SPREADSHEET_ID"])
    except KeyError:
        raise RuntimeError("SPREADSHEET_ID environment variable not set")
    sheet_name = __import__("os").environ.get("SHEET_NAME", "blogs to read")
    return spreadsheet.worksheet(sheet_name)


def load_articles() -> List[Article]:
    """Return all rows in the sheet as a list of ``Article`` objects."""

    worksheet = _get_worksheet()
    raw_rows = worksheet.get_all_records()
    articles: List[Article] = []
    for row_number, row in enumerate(raw_rows, start=2):
        articles.append(Article.from_dict(row, row_number))
    return articles


def ensure_column(worksheet: gspread.Worksheet, name: str) -> int:
    """Ensure the first row contains ``name``.

    Returns the 1‑based column index corresponding to the header.  If the
    header was missing it is appended, and the first row is rewritten in a
    single update call.
    """
    headers = worksheet.row_values(1)
    if name in headers:
        return headers.index(name) + 1
    headers.append(name)
    worksheet.update("1:1", [headers])
    return len(headers)


def update_article(article: Article) -> None:
    """Backward-compatible one-row updater retained for tests or scripts.

    This is now implemented on top of :func:`apply_updates` by wrapping a
    single-article list.  We keep it around so earlier code and tests that
    reference it continue to work.
    """
    apply_updates([article])


def apply_updates(articles: List[Article]) -> None:
    """Write all provided ``articles`` back to the sheet in one batch.

    Columns that don't yet exist are created once, and then a single
    ``worksheet.update`` call writes the body rows.  Every ``Article`` object
    should have ``row_number`` set; entries without it are ignored.
    """
    if not articles:
        return

    worksheet = _get_worksheet()
    # ensure we have all the headers we might write
    headers = worksheet.row_values(1)
    needed = [
        "title", "url", "reading_time_min", "error", "word_count",
        "fetched_at", "last_attempted", "category",
        "created_at", "created_by", "updated_at", "updated_by",
    ]
    for name in needed:
        if name not in headers:
            headers.append(name)
    if len(headers) != len(worksheet.row_values(1)):
        worksheet.update("1:1", [headers])

    # map header to index for building rows
    header_to_index = {h: i for i, h in enumerate(headers)}
    # build list-of-lists for values; skip articles without row_number
    rows = []
    for art in articles:
        if art.row_number is None:
            continue
        # make a row aligned with headers
        row = [""] * len(headers)
        for key, val in art.to_dict().items():
            if val is None:
                continue
            idx = header_to_index.get(key)
            if idx is not None:
                row[idx] = val
        rows.append(row)
    if not rows:
        return
    start = 2
    end = start + len(rows) - 1
    rng = f"A{start}:{chr(ord('A')+len(headers)-1)}{end}"
    worksheet.update(rng, rows)
