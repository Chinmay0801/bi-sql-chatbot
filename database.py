"""Runs SQL against banking.db and returns results as pandas DataFrames."""

import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = "banking.db"

engine = create_engine(f"sqlite:///{DB_PATH}")


def run_query(sql: str) -> pd.DataFrame:
    """Execute a SQL string against banking.db and return the results."""
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn)


def get_schema() -> str:
    """Return the CREATE TABLE statements for every table, for prompting the LLM."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table'")
        ).fetchall()
    return "\n\n".join(row[0] for row in rows if row[0])


if __name__ == "__main__":
    print(get_schema())
    print()
    df = run_query(
        """
        SELECT region, COUNT(*) AS branch_count
        FROM branches
        GROUP BY region
        ORDER BY branch_count DESC
        """
    )
    print(df)
