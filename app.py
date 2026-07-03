"""Streamlit UI: ask a question in English, see the generated SQL and results."""

import streamlit as st

from database import get_schema, run_query
from llm import generate_sql
from safety import enforce_row_limit, is_safe

st.set_page_config(page_title="BI SQL Chatbot", layout="wide")

st.title("BI SQL Chatbot")
st.caption("Ask the banking database a question in plain English.")

with st.expander("Sample questions"):
    st.markdown(open("sample_questions.md").read())

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

    with st.expander("Generated SQL", expanded=True):
        st.code(sql, language="sql")

    try:
        df = run_query(sql)
    except Exception as e:
        st.error(f"The query ran but failed: {e}")
        st.stop()

    st.dataframe(df, use_container_width=True)
