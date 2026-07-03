# BI SQL Chatbot

Ask a banking database questions in plain English and get back a table (and soon, a chart) — an LLM writes the SQL for you.

**Status:** work in progress. Phases 0-2 of the build roadmap are done (project setup, synthetic banking database, query runner). LLM integration, the Streamlit UI, safety checks, and charts are next.

## What's here so far

- `build_database.py` — generates `banking.db`, a SQLite database with 5 tables (`customers`, `accounts`, `transactions`, `branches`, `loans`) filled with realistic fake data via Faker.
- `database.py` — runs SQL against `banking.db` via SQLAlchemy and returns a pandas DataFrame; also exposes the schema as text for prompting an LLM.
- `sample_questions.md` — a list of demo questions the schema can answer.

## Setup

```bash
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python build_database.py    # generates banking.db
python database.py          # sanity-check: prints schema + a sample query
```

Copy your Groq API key into `.env` (see `.env` placeholder) before Phase 3.

## Roadmap

See the full project plan for architecture, tech stack rationale, and the remaining phases (English → SQL via Groq, Streamlit UI, safety validation, auto-charting).
