"""Validates that generated SQL is a single, read-only SELECT statement."""

import re

import sqlglot
from sqlglot import expressions as exp

# Read-only statement types: plain SELECTs and set operations (UNION /
# INTERSECT / EXCEPT). Newer sqlglot groups set ops under SetOperation;
# older versions make Intersect/Except subclasses of Union.
_READ_ONLY = (exp.Select, getattr(exp, "SetOperation", exp.Union))


def is_safe(sql: str) -> tuple[bool, str]:
    """Return (True, "") if sql is a single safe SELECT, else (False, reason)."""
    try:
        statements = sqlglot.parse(sql, dialect="sqlite")
    except Exception as e:
        return False, f"could not parse SQL: {e}"

    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        return False, "only a single SQL statement is allowed"

    if not isinstance(statements[0], _READ_ONLY):
        return False, "only SELECT queries are allowed"

    return True, ""


def enforce_row_limit(sql: str, max_rows: int = 1000) -> str:
    """Append a LIMIT clause if the query doesn't already have one."""
    if re.search(r"\blimit\b", sql, re.IGNORECASE):
        return sql
    return sql.rstrip().rstrip(";") + f" LIMIT {max_rows}"
