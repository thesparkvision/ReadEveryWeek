#!/usr/bin/env python3
"""Thin entrypoint for the ReadEveryWeek reading‑time estimator."""

import argparse
import logging

from read_every_week import pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="estimate reading times in a sheet")
    parser.add_argument("--write", action="store_true",
                        help="actually write updates to the sheet (dry run by default)")
    parser.add_argument("--retry-errors", action="store_true",
                        help="re‑attempt URLs that previously failed")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s\n",
    )

    pipeline.run(dry_run=not args.write, retry_errors=args.retry_errors)


if __name__ == "__main__":
    main()
