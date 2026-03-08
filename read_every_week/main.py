#!/usr/bin/env python3
"""Thin entrypoint for the ReadEveryWeek reading‑time estimator."""

import argparse
import os
import logging

from read_every_week import pipeline


def cli() -> None:
    parser = argparse.ArgumentParser(description="estimate reading times in a sheet")
    parser.add_argument("--write", action="store_true",
                        help="actually write updates to the sheet (dry run by default)")
    parser.add_argument("--retry-errors", action="store_true",
                        help="re‑attempt URLs that previously failed")
    args = parser.parse_args()

    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    pipeline.run(dry_run=not args.write, retry_errors=args.retry_errors)

def run():
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    is_dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    retry_errors = os.getenv("RETRY_ERRORS", "false").lower() == "true"
    pipeline.run(dry_run=is_dry_run, retry_errors=retry_errors)

run()