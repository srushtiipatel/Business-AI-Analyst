import streamlit as st
import pandas as pd
import zipfile
import io
from sqlalchemy import text, inspect
import re
from database.db import get_engine
from llm.gemini import generate_summary

st.set_page_config(page_title="Upload Dataset", layout="wide")
st.title("📁 Upload Your Business Dataset")

def clean_table_name(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    return name[:50]

def fix_strict_ooxml(file_bytes: bytes) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zin:
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.endswith('.xml') or item.filename.endswith('.rels'):
                    text_content = data.decode('utf-8', errors='replace')
                    text_content = text_content.replace(
                        'http://purl.oclc.org/ooxml/spreadsheetml/main',
                        'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
                    ).replace(
                        'http://purl.oclc.org/ooxml/officeDocument/relationships',
                        'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                    ).replace(
                        'http://purl.oclc.org/ooxml/drawingml/2006/main',
                        'http://schemas.openxmlformats.org/drawingml/2006/main'
                    )
                    data = text_content.encode('utf-8')
                zout.writestr(item, data)
    buf.seek(0)
    return buf

def read_file(uploaded_file) -> pd.DataFrame:
    file_bytes = uploaded_file.read()
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    else:
        try:
            return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        except Exception:
            fixed = fix_strict_ooxml(file_bytes)
            return pd.read_excel(fixed, engine='openpyxl')

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        df = read_file(uploaded_file)
        st.success(f"✅ Loaded: {uploaded_file.name}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing Values", int(df.isnull().sum().sum()))
        c4.metric("File Size", f"{uploaded_file.size // 1024} KB")

        with st.expander("📊 Column Details"):
            st.dataframe(pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.values,
                "Non-Null Count": df.count().values,
                "Null Count": df.isnull().sum().values
            }), use_container_width=True)

        st.subheader("Preview (first 5 rows)")
        st.dataframe(df.head(), use_container_width=True)

        table_name = clean_table_name(uploaded_file.name.rsplit(".", 1)[0])
        st.info(f"Table name: `{table_name}`")

        if st.button("💾 Save to Database", type="primary"):
            engine = get_engine()

            # ✅ SQLite compatible table existence check
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()

            if table_name in existing_tables:
                st.warning(f"Table `{table_name}` already exists. Delete `bi_copilot.db` to re-upload.")
            else:
                df.to_sql(table_name, engine, if_exists="replace", index=False)
                st.success(f"✅ Saved `{table_name}` with {len(df)} rows!")
                st.session_state["active_table"] = table_name

            with st.spinner("🤖 Generating AI summary..."):
                df_info = f"Columns: {list(df.columns)}\nShape: {df.shape}\nSample:\n{df.head(3).to_string()}"
                summary = generate_summary(df_info)
                st.subheader("🤖 AI Dataset Summary")
                st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")