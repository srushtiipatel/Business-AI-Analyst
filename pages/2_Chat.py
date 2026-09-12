import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text
from database.db import get_engine, get_table_schema, get_all_tables, run_query
from llm.gemini import generate_sql, generate_insights, suggest_questions
import re

st.set_page_config(page_title="Chat with Data", layout="wide")
st.title("💬 Ask Your Business Data")

tables = get_all_tables()
if not tables:
    st.warning("⚠️ No tables found. Please upload a dataset first.")
    st.stop()

table = st.selectbox("📂 Select dataset", tables)
schema = get_table_schema(table)

# ── Suggested questions ──────────────────────────────────────
with st.expander("💡 Need inspiration? Click to get suggested questions"):
    if st.button("✨ Generate Suggested Questions"):
        with st.spinner("Thinking..."):
            suggestions = suggest_questions(schema)
            st.write(suggestions)

st.markdown("---")

# ── Question input ────────────────────────────────────────────
question = st.text_input(
    "🔍 Ask a question about your data",
    placeholder="e.g. What is the average credit score by employment status?"
)

def is_safe_sql(sql: str) -> bool:
    banned = ["insert", "update", "delete", "drop", "alter", "truncate", "create"]
    return not any(word in sql.lower() for word in banned)

def clean_sql(sql: str) -> str:
    sql = re.sub(r"```sql|```", "", sql).strip()
    # Remove any extra text before SELECT
    match = re.search(r"(SELECT|WITH)\s", sql, re.IGNORECASE)
    if match:
        sql = sql[match.start():]
    return sql.strip()

def auto_chart(df: pd.DataFrame, question: str):
    """Smartly pick the best chart based on data shape and question keywords."""
    if df.empty or df.shape[1] < 2:
        return

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    q_lower = question.lower()

    # Detect chart type from question keywords
    is_trend     = any(w in q_lower for w in ["trend", "over time", "month", "monthly", "year", "daily"])
    is_compare   = any(w in q_lower for w in ["compare", "vs", "versus", "difference", "between"])
    is_dist      = any(w in q_lower for w in ["distribution", "spread", "range", "histogram"])
    is_pie       = any(w in q_lower for w in ["percentage", "proportion", "share", "ratio", "breakdown"])
    is_scatter   = any(w in q_lower for w in ["relationship", "correlation", "impact", "affect"])

    fig = None

    try:
        if df.shape[0] == 1:
            # Single row — show as metric cards
            st.subheader("📊 Result")
            cols = st.columns(len(df.columns))
            for i, col in enumerate(df.columns):
                cols[i].metric(col, df.iloc[0][col])
            return

        elif is_scatter and len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                           color=cat_cols[0] if cat_cols else None,
                           title=f"Scatter: {num_cols[0]} vs {num_cols[1]}",
                           template="plotly_dark")

        elif is_pie and cat_cols and num_cols:
            fig = px.pie(df, names=cat_cols[0], values=num_cols[0],
                        title=f"Distribution of {num_cols[0]} by {cat_cols[0]}",
                        template="plotly_dark")

        elif is_trend and num_cols:
            x_col = cat_cols[0] if cat_cols else df.columns[0]
            fig = px.line(df, x=x_col, y=num_cols[0],
                         markers=True,
                         title=f"Trend: {num_cols[0]} over {x_col}",
                         template="plotly_dark")

        elif is_dist and num_cols:
            fig = px.histogram(df, x=num_cols[0],
                              title=f"Distribution of {num_cols[0]}",
                              template="plotly_dark")

        elif cat_cols and num_cols:
            if df.shape[0] <= 15:
                fig = px.bar(df, x=cat_cols[0], y=num_cols[0],
                            color=cat_cols[0],
                            title=f"{num_cols[0]} by {cat_cols[0]}",
                            template="plotly_dark",
                            text_auto=True)
            else:
                fig = px.line(df, x=cat_cols[0], y=num_cols[0],
                             markers=True,
                             title=f"{num_cols[0]} over {cat_cols[0]}",
                             template="plotly_dark")

        elif len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                           title=f"{num_cols[0]} vs {num_cols[1]}",
                           template="plotly_dark")

        if fig:
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

    except Exception:
        st.dataframe(df, use_container_width=True)

def save_to_history(question, sql, table, insights):
    try:
        engine = get_engine()
        with engine.connect() as conn:
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
            conn.execute(text("""
                INSERT INTO query_history (question, sql_query, table_name, insights)
                VALUES (:q, :s, :t, :i)
            """), {"q": question, "s": sql, "t": table, "i": insights})
            conn.commit()
    except Exception:
        pass  # Don't break the UI if history save fails

# ── Main flow ─────────────────────────────────────────────────
if question:
    with st.spinner("🤖 Generating SQL..."):
        raw_sql = generate_sql(question, schema)
        sql = clean_sql(raw_sql)

    st.subheader("🧠 Generated SQL")
    st.code(sql, language="sql")

    if not is_safe_sql(sql):
        st.error("🚫 Unsafe query detected. Only SELECT statements are allowed.")
        st.stop()

    try:
        rows, keys = run_query(sql)
        df_result = pd.DataFrame(rows, columns=keys)

        st.subheader(f"📋 Results — {len(df_result)} rows")
        st.dataframe(df_result, use_container_width=True)

        if not df_result.empty and df_result.shape[0] > 1:
            st.subheader("📈 Chart")
            auto_chart(df_result, question)

        # AI Insights
        if not df_result.empty:
            with st.spinner("💡 Generating business insights..."):
                insights = generate_insights(
                    question, sql,
                    df_result.head(10).to_string()
                )

            st.subheader("🤖 Business Insights")
            for line in insights.strip().split("\n"):
                if line.strip():
                    st.info(f"💡 {line.strip()}")

            save_to_history(question, sql, table, insights)

        # ── Export buttons ────────────────────────────────────
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            csv = df_result.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download CSV",
                csv, "result.csv", "text/csv",
                use_container_width=True
            )

        with col2:
            import io
            excel_io = io.BytesIO()
            with pd.ExcelWriter(excel_io, engine="xlsxwriter") as writer:
                df_result.to_excel(writer, index=False, sheet_name="Results")
            st.download_button(
                "⬇️ Download Excel",
                excel_io.getvalue(),
                "result.xlsx",
                "application/vnd.ms-excel",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ Query error: {e}")
        st.info("💬 Try rephrasing your question.")