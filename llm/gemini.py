from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "qwen/qwen3.8-27b"  # Free, fast, excellent SQL generation

def _ask(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def generate_sql(question: str, schema: str) -> str:
    prompt = f"""You are an expert SQL assistant. Convert the user's question into a valid SQLite SELECT query.

{schema}

Rules:
- Only generate SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
- Use exact column names from the schema above.
- ALWAYS include the category/group column in SELECT when using GROUP BY. Example: SELECT Employment_Status, AVG(Credit_Score) not just AVG(Credit_Score).
- Return ONLY the raw SQL query, no explanation, no markdown, no backticks.

Question: {question}
SQL:"""
    return _ask(prompt)

def generate_summary(df_info: str) -> str:
    prompt = f"""You are a data analyst. Given this dataset info, write a short business summary (5-6 sentences).
Describe what the dataset is about, key columns, and suggest 4 useful business questions.

Dataset info:
{df_info}

Keep it concise and business-friendly."""
    return _ask(prompt)

def generate_insights(question: str, sql: str, result_preview: str) -> str:
    prompt = f"""You are a business intelligence analyst. A user asked a question and got this data result.
Write 3-4 short business insights. Highlight trends, comparisons, or anomalies. Be actionable.

User question: {question}
SQL used: {sql}
Result preview:
{result_preview}

Keep each insight to 1-2 sentences."""
    return _ask(prompt)

def suggest_questions(schema: str, last_question: str = "") -> str:
    prompt = f"""Based on this database schema, suggest 5 useful business questions a user can ask.
{f'The user just asked: {last_question}' if last_question else ''}

{schema}

Return only a numbered list of 5 questions. No extra text."""
    return _ask(prompt)