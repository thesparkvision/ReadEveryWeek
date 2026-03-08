from pathlib import Path
from jinja2 import Template
import os
import requests
from datetime import datetime

from .models import Article

TEMPLATE = Template(
    Path("read_every_week/templates/recommendations.html").read_text()
)

RESEND_ENDPOINT = "https://api.resend.com/emails"


def subject_for_today():
    weekday = datetime.now().strftime("%A")

    subjects = {
        "Monday": "Light Monday Reading",
        "Thursday": "Midweek Reading",
        "Saturday": "Weekend Deep Reads",
        "Sunday": "Sunday Reading",
    }

    return subjects.get(weekday, "Today's Reading")


def render_email(primary, worthies):
    return TEMPLATE.render(
        subject=subject_for_today(),
        primary=primary,
        worthies=worthies,
        total_minutes=sum(a.reading_time_min for a in primary),
    )


def send_recommendation_email(primary, worthies):

    if not primary:
        return False

    html = render_email(primary, worthies)

    payload = {
        "from": os.environ["EMAIL_FROM"],
        "to": [os.environ["EMAIL_TO"]],
        "subject": subject_for_today(),
        "html": html,
    }

    r = requests.post(
        RESEND_ENDPOINT,
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=10,
    )

    return r.status_code in (200, 201)
