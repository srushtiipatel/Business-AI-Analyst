# 🧠 Business AI Analyst

A free, open-source AI tool that lets anyone analyse business data 
by asking questions in plain English — no SQL or coding knowledge required.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red)
![Groq](https://img.shields.io/badge/LLM-Groq%20%2B%20Qwen-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Live Demo
> [Click here to try it live](https://yourusername-business-ai-analyst.streamlit.app)

---

## 💡 What is Business AI Analyst?

Business AI Analyst is a web application where you:
1. Upload any CSV or Excel business dataset
2. Ask questions about it in plain English
3. Get accurate SQL queries generated automatically
4. See interactive charts and graphs
5. Read AI-written business insights and recommendations
6. Export results as CSV or Excel

No SQL knowledge needed. No coding required. Just ask and get answers.

---

## 🛠️ Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| Frontend + Backend | Streamlit | Free |
| AI / LLM | Groq API + Qwen 27B | Free |
| Database | SQLite | Free |
| Data Processing | Pandas | Free |
| Visualization | Plotly | Free |
| Export | XlsxWriter | Free |

**Total cost: $0 — completely free forever**

---

## ✨ Features

### 📁 Dataset Upload
- Upload CSV or Excel files
- Auto detects column types
- Shows missing values, row count, column info
- Auto creates database table from your file
- AI generates a business summary of your dataset

### 💬 Ask Questions in Plain English
- Type any business question naturally
- AI converts it to accurate SQL automatically
- Results shown as interactive table
- Only SELECT queries allowed — your data is safe

### 📈 Smart Charts
- Automatically picks the right chart for your data
- Bar charts for comparisons
- Line charts for trends
- Pie charts for proportions
- Scatter plots for relationships
- Histograms for distributions

### 🤖 Business Insights
- AI analyses your results
- Writes 3-4 actionable business insights
- Highlights trends, risks, and opportunities

### 🕑 Query History
- All questions and results saved
- Revisit any previous analysis

### ⬇️ Export
- Download results as CSV
- Download results as Excel

---

## 📂 Project Structure

Business AI Analyst/
│
├── .vscode/
│   └── settings.json
│
├── database/
│   └── db.py
│
├── llm/
│   └── gemini.py
│
├── pages/
│   ├── 1_Upload.py
│   ├── 2_Chat.py
│   └── 3_History.py
│
├── .env
├── app.py
├── bi_copilot.db
├── README.md
└── requirements.txt