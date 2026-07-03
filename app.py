"""Streamlit UI: ask a question in English, see the generated SQL, results, and a chart."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_schema, run_query
from llm import generate_sql
from safety import enforce_row_limit, is_safe

PROJECT_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="BI SQL Chatbot", layout="wide")

st.title("BI SQL Chatbot")
st.caption("Ask the banking database a question in plain English.")


def auto_chart(df: pd.DataFrame):
    """Return a Plotly figure if the result shape suits one, else None.

    Heuristic: one categorical/text column on the x-axis, first numeric
    column on the y-axis. Skips single-column results, single-row results
    (e.g. "what is the total balance?"), and high-cardinality categories.
    """
    if len(df) < 2 or len(df.columns) < 2:
        return None

    numeric_cols = df.select_dtypes("number").columns.tolist()
    other_cols = [c for c in df.columns if c not in numeric_cols]
    if not numeric_cols or not other_cols:
        return None

    x, y = other_cols[0], numeric_cols[0]
    if df[x].nunique() > 30:
        return None

    if pd.api.types.is_datetime64_any_dtype(df[x]):
        return px.line(df, x=x, y=y)
    return px.bar(df, x=x, y=y)


with st.expander("Sample questions"):
    st.markdown((PROJECT_DIR / "sample_questions.md").read_text())

question = st.text_input(
    "Your question",
    placeholder="e.g. Which 5 branches have the highest total account balance?",
)

if st.button("Ask", type="primary") and question:
    with st.spinner("Generating SQL..."):
        try:
            sql = generate_sql(question, get_schema())
        except Exception as e:
            st.error(f"Could not generate SQL: {e}")
            st.stop()

    safe, reason = is_safe(sql)
    if not safe:
        st.error(f"Generated query was rejected for safety ({reason}).")
        st.code(sql, language="sql")
        st.stop()

    sql = enforce_row_limit(sql)

    try:
        df = run_query(sql)
    except Exception as e:
        st.error(f"The query ran but failed: {e}")
        st.code(sql, language="sql")
        st.stop()

    # Persist so the result survives Streamlit reruns (widget interactions).
    st.session_state["result"] = {"question": question, "sql": sql, "df": df}

result = st.session_state.get("result")
if result:
    st.markdown(f"**{result['question']}**")

    with st.expander("Generated SQL", expanded=True):
        st.code(result["sql"], language="sql")

    st.dataframe(result["df"], use_container_width=True)

    fig = auto_chart(result["df"])
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
