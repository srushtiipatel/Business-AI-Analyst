import streamlit as st
from database.db import get_engine, get_all_tables, get_table_schema
from sqlalchemy import text
import pandas as pd

st.set_page_config(
    page_title="Business AI Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: bold; }
.stButton > button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("📊 AI Business Intelligence Copilot")
st.caption("Powered by Groq · LLaMA 3.1 · SQLite · Plotly — 100% Free")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────
engine = get_engine()
tables = get_all_tables()

if tables:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📁 Datasets Loaded", len(tables))

    try:
        with engine.connect() as conn:
            total_queries = conn.execute(
                text("SELECT COUNT(*) FROM query_history")
            ).scalar()
        c2.metric("💬 Total Queries Asked", total_queries)
    except:
        c2.metric("💬 Total Queries Asked", 0)

    # Count total rows across all tables
    total_rows = 0
    for t in tables:
        try:
            with engine.connect() as conn:
                count = conn.execute(text(f'SELECT COUNT(*) FROM "{t}"')).scalar()
                total_rows += count
        except:
            pass
    c3.metric("🗃️ Total Records", f"{total_rows:,}")
    c4.metric("🤖 AI Model", "LLaMA 3.1")

    st.markdown("---")

    # ── Dataset preview cards ──────────────────────────────────
    st.subheader("📂 Your Datasets")
    for t in tables:
        with st.expander(f"📋 {t}"):
            try:
                df = pd.read_sql(f'SELECT * FROM "{t}" LIMIT 5', engine)
                st.dataframe(df, use_container_width=True)
                schema = get_table_schema(t)
                st.code(schema, language="text")
            except Exception as e:
                st.error(str(e))
else:
    st.info("👈 No datasets yet. Go to **Upload** page to get started!")
    st.markdown("""
    ### How it works
    1. 📁 **Upload** any CSV or Excel file
    2. 💬 **Ask** questions in plain English
    3. 📈 **Get** SQL + charts + AI insights automatically
    4. ⬇️ **Export** results as CSV or Excel
    """)