---
title: FinAI-Agent
emoji: 💰
colorFrom: indigo
colorTo: green
sdk: streamlit
app_file: app.py
python_version: "3.13"    # ← specify your Python version
pinned: false
---

# Finance-Agent 🤖💰

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 What Is This?

**Finance-Agent** is your chat-native **CFO co-pilot**.  
Ask plain-English questions about your company’s Excel ledger, and get **instant answers with context + charts**.

![Demo](content/img.png)

### Example

You ➜ “Compare EBITDA and cash runway for Q1 vs Q2, convert EUR to USD.”

Agent ➜ “EBITDA Q1: $1.42 M, Q2: $1.65 M (+16.4 %).

Cash runway improved from 7.1 → 8.3 months.”

---

## ✨ Feature Tour
- **Natural-Language Querying** — Gemini 2.5 Flash interprets finance jargon and casual questions alike.  
- **Dynamic Tool Routing** — LangChain React agent picks one or more of 7 custom Python tools (revenue variance, gross-margin %, OpEx breakdown…).  
- **Smart Currency Handling** — Detects EUR rows, fetches FX sheet, normalizes to USD.  
- **Date Inference** — “This year”, “last 3 months”, “Jun’25” → precise periods.  
- **Chart Factory** — Generates PNGs via Matplotlib (line, bar, area, stacked).  
- **Streamlit UI** — Slack-style sidebar, message persistence, spinner feedback.  
- **Excel Plug-and-Play** — Works with a single `data.xlsx` containing 4 sheets: `actuals`, `budget`, `cash`, `fx`.  
- **Fallback PythonREPL** — If no tool fits, agent writes ad-hoc Pandas code.  
- **Pytest Suite** — Automated tests for tool selection, calc accuracy, caching, and rendering.  
- **One-click Deploy** — Just `streamlit run app.py`.  

---

## 🏗️ Architecture
```text
┌──────── Chat UI (Streamlit) ───────┐
│  User Input + Chat History         │
│      ↓ finance_agent.invoke()      │
└────────────────────────────────────┘
                │
                ▼
┌── LangChain AgentExecutor ──────────────┐
│  Prompt (system + history + input)      │
│  LLM: Gemini 2.5 Flash                  │
│  React tool-calling loop                │
└──────────────┬──────────────────────────┘
               │ selects & runs
┌──────────────┴──────────────────────────┐
│  Custom Tools                           │
│  • get_revenue_variance                 │
│  • get_gross_margin_pct                 │
│  • get_opex_breakdown                   │
│  • get_ebitda_proxy                     │
│  • get_cash_runway                      │
│  • plot_chart                           │
│  • code_analysis (PythonREPL)           │
└─────────────────────────────────────────┘
```
---

## 📂 Folder Structure
```text
finance-agent/
├─ agent/
│  ├─ agent.py        # creates cached AgentExecutor
│  ├─ utils.py        # numeric calculations
│  └─ tests/          # pytest suite
├─ data.xlsx          # sample ledger
├─ app.py             # Streamlit front-end
├─ requirements.txt
└─ .streamlit/
   └─ secrets.toml    # custom theme & font
```
---

## ⚙️ Installation

```bash
git clone https://github.com/Sbboss/FinAIAgent.git
cd FinAIAgent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
🏃 Quick Start

Drop your company ledger into data.xlsx with sheets: actuals, budget, cash, fx.

1. Run the app:
```bash
streamlit run app.py
```
2. Ask away:
```
“Trend gross margin % monthly for 2024.”
“Why did revenue miss budget in Nov 25?”
“How many months of runway if burn stays flat?”
```
👉 Charts appear inline; numeric answers include deltas vs budget and YOY.

___

🔬 Testing
```
pytest -v
```
Covers:
Tool parameter validation
Correct tool selection via intermediate steps
Currency conversion accuracy
Streamlit image rendering
Caching behaviour (st.cache_resource)

---

🛠️ Configuration

| Setting                | File / Env               | Default               |
| ---------------------- | ------------------------ | --------------------- |
| Google Gemini API key  | `GOOGLE_API_KEY`         | put in `secrets.toml` |
| Excel file path        | `data.xlsx`              | —                     |
| LLM temperature        | agent                    | `0.2`                 |

---

🌅 Roadmap

* 🔄 CSV and SQL connectors
* 🗃️ Vector memory for conversation continuity
* 🌐 Multi-LLM failover (Gemini → GPT-4o)
* 📈 Automatic dashboard snapshots to PDF
* 💬 Slack / Teams integration
* 🎥 Demo GIF: live chat → chart → answer

---

🙌 Contributing

1. Fork & branch (feat/your-feature)
2. Add tests (pytest -k your_test)
3. Submit PR with concise description
   
✅ All significant changes must pass CI and keep coverage ≥ 95%.

---

📝 License
MIT — see [LICENSE](LICENSE)
Finance-Agent turns spreadsheets into strategy. Ask. Analyze. Act. ⚡

--- 
