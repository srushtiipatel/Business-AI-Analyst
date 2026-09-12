import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.db import get_engine

st.set_page_config(page_title="Query History", layout="wide")
st.title("🕑 Query History")

try:
    engine = get_engine()
    with engine.connect() as conn:
        # Create table if it doesn't exist yet
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                sql_query TEXT,
                table_name TEXT,
                insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

        rows = conn.execute(text(
            "SELECT question, sql_query, table_name, insights, created_at FROM query_history ORDER BY created_at DESC LIMIT 50"
        )).fetchall()

    if not rows:
        st.info("No queries yet. Go to Chat page and ask something!")
    else:
        for row in rows:
            # SQLite returns created_at as string, PostgreSQL as datetime
            # str()[:16] works for both
            timestamp = str(row[4])[:16]
            with st.expander(f"❓ {row[0]} — {timestamp}"):
                st.code(row[1], language="sql")
                st.caption(f"Table: {row[2]}")
                if row[3]:
                    st.write("**Insights:**", row[3])

except Exception as e:
    st.error(f"Could not load history: {e}")