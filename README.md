# BI SQL Chatbot

Ask a banking database questions in plain English. An LLM translates your question into SQL, a safety layer validates it, and the app returns the results as a table with an auto-generated chart.

> "Which 5 branches have the highest total account balance?" → SQL → table + bar chart, in seconds, no SQL knowledge needed.

## How it works

```
English question
      │
      ▼
Groq LLM (llm.py) ── schema-aware prompt, returns raw SQL
      │
      ▼
Safety check (safety.py) ── sqlglot parse: single read-only
      │                     SELECT/UNION only, LIMIT enforced
      ▼
SQLite (database.py) ── query runs against banking.db,
      │                 results as a pandas DataFrame
      ▼
Streamlit UI (app.py) ── generated SQL + results table
                         + auto-picked Plotly chart
```

## The database

`banking.db` is a synthetic SQLite database (seeded, reproducible) built by `build_database.py` using Faker:

| Table | Rows | Contents |
|---|---|---|
| `branches` | 15 | branch name, city, region |
| `customers` | 1,000 | demographics, join date, income bracket |
| `accounts` | 1,500 | type, balance, open date, branch |
| `transactions` | 50,000 | date, amount, credit/debit, spending category |
| `loans` | 400 | type, principal, interest rate, status |

See `sample_questions.md` for questions the schema can answer.

## Safety

Generated SQL is never trusted blindly:

- Parsed with sqlglot; anything unparseable is rejected.
- Only a single statement allowed — no piggy-backed second statement.
- Only read-only statements (SELECT and UNION/INTERSECT/EXCEPT); INSERT/UPDATE/DELETE/DROP are rejected.
- A `LIMIT 1000` is appended if the query has none.

## Setup

```bash
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python build_database.py    # generates banking.db (skip if it exists)
```

Create `.env` in the project root with your [Groq API key](https://console.groq.com/keys):

```
GROQ_API_KEY=your_key_here
```

## Run

```bash
streamlit run app.py
```

Opens at http://localhost:8501.

## Tech stack

Python · Streamlit · Groq API (Llama 3.3 70B) · SQLite · SQLAlchemy · pandas · sqlglot · Plotly · Faker

## Roadmap

- [ ] Migrate off `llama-3.3-70b-versatile` (Groq shuts it down 2026-08-16; use `openai/gpt-oss-120b` or `qwen/qwen3.6-27b`)
- [ ] Chat-style history: keep past Q&A on screen, allow follow-up questions with context
- [ ] Self-correction loop: on SQL error, feed the error back to the LLM for one retry
- [ ] Few-shot examples in the prompt to improve SQL accuracy
- [ ] Let the user pick/override the chart type
- [ ] Evaluation set: golden question→SQL pairs to measure accuracy on every prompt change
- [ ] CSV download button for results
