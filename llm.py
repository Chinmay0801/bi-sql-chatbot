"""Turns an English question into a SQL query, using the Groq API."""

import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are a SQL expert for a SQLite banking database. Given the
database schema and a question in plain English, write a single SQL query that
answers it.

Rules:
- Output ONLY the SQL query, no explanation, no markdown code fences.
- Only ever write a SELECT statement. Never write INSERT, UPDATE, DELETE, DROP,
  ALTER, or any other statement that modifies data or schema.
- Use only the tables and columns given in the schema below.
- If the question is ambiguous, make a reasonable assumption and answer it anyway.

Schema:
{schema}
"""


def _strip_code_fences(text: str) -> str:
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()


def generate_sql(question: str, schema: str) -> str:
    """Ask the LLM to translate an English question into a SQL query string."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(schema=schema)},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    raw_sql = response.choices[0].message.content
    return _strip_code_fences(raw_sql)


if __name__ == "__main__":
    from database import get_schema

    question = "Which 5 branches have the highest total account balance?"
    sql = generate_sql(question, get_schema())
    print("Question:", question)
    print("Generated SQL:\n", sql)
