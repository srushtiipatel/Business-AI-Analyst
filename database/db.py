from sqlalchemy import create_engine, text, inspect
import os

# SQLite - creates a file called bi_copilot.db in your project folder
DATABASE_URL = "sqlite:///bi_copilot.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_engine():
    return engine

def get_table_schema(table_name: str) -> str:
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    schema = f"Table: {table_name}\nColumns:\n"
    for col in columns:
        schema += f"  - {col['name']} ({col['type']})\n"
    return schema

def get_all_tables() -> list:
    inspector = inspect(engine)
    # Exclude internal history table from dataset list
    all_tables = inspector.get_table_names()
    return [t for t in all_tables if t != "query_history"]

def run_query(sql: str):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        keys = list(result.keys())
    return rows, keys