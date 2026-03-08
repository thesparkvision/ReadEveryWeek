# ReadEveryWeek
Making a personal reading recommender to read more and gamify the experience.

This project helps one capture articles, read them deeply, mark what truly mattered,
and reflect on how the reading shaped the thinking over time.

It is:
- Single-user
- Private by default

## Why this exists

[Read this here](https://github.com/thesparkvision/ReadEveryWeek/blob/main/WhyThisExists.md)

## Core loop

Capture → Read → Mark → Revisit → Reflect

## Current Architecture

                ┌─────────────────────┐
                │   Article Sources   │
                │ (Hardcoded URLs)    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Python Script     │
                │  (main.py / cli)    │
                └──────────┬──────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
 ┌──────────────┐  ┌───────────────┐  ┌───────────────┐
 │ Fetch HTML   │  │ Extract Text  │  │ Reading Time  │
 │ (requests)   │  │ (article lib) │  │ (words/200)   │
 └──────────────┘  └───────────────┘  └───────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Email HTML Builder  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Email Sender        │
                │ (SMTP / API)        │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Your Inbox         │
                │  ReadEveryWeek Mail │
                └─────────────────────┘
                
## Roadmap

### Phase 1 — Doc → Sheet/Raindrop → Recommendations
Automated ingestion and editorial recommendations.

### Phase 2 — Reading Interface
Mobile-first web reader with navigation and notes.

### Phase 3 — Persistence & Deployment
Database as an enhancement, Sheet always supported.

### Phase 4 — Mobile App
Thin client over the same API.

### Phase 5 — Intelligence & Reflection
Summaries, insights, stats, yearly reflection.


## Status

This is a side project that I am working on, in my free time. It might get abandoned but it might be continued too.

