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

st.title("📊  Business AI Analyst ")
st.caption("Upload any business dataset → Ask questions in plain English → Get SQL + Charts + Insights automatically")
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
    c4.metric("🤖 AI Model", "Qwen 27B")

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

st.markdown("---")
st.subheader("⚙️ Settings")

col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ Clear Query History", type="secondary"):
        try:
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM query_history"))
                conn.commit()
            st.success("✅ Query history cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("⚠️ Delete All Datasets", type="secondary"):
        confirm = st.checkbox("I understand this will delete all my data")
        if confirm:
            try:
                # Drop all tables except query_history
                all_tables = get_all_tables()
                with engine.connect() as conn:
                    for t in all_tables:
                        conn.execute(text(f'DROP TABLE IF EXISTS "{t}"'))
                    conn.commit()
                st.success("✅ All datasets deleted!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

