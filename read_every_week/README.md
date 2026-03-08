# read_every_week package

This directory contains the core library for the reading‑time estimator.
The helper script `estimate_reading_time.py` sits here as the entrypoint.

## Environment variables

The code looks for the following environment variables at runtime:

* `SPREADSHEET_ID` **(required)**
  - The ID of the Google Sheet to operate on.  You can find this in the
    document URL after `/d/` and before `/edit`.
  - Example: `export SPREADSHEET_ID="1AbCdEfGhIjKlMnOp"`

* `SHEET_NAME` (optional)
  - The name of the tab within the spreadsheet.  Defaults to `"blogs to read"`
    if not supplied.
  - Example: `export SHEET_NAME="Links"`

* `GOOGLE_SERVICE_ACCOUNT_JSON` (recommended for cloud service accounts)
  - service‑account JSON data of google cloud project

* `RESEND_API_KEY` - for integration with Resend mail service

* `EMAIL_FROM` - for setting the sender's email

* `EMAIL_TO` - for setting the email receiver if for a single user

