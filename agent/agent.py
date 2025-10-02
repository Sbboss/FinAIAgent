import streamlit as st
import sys
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_experimental.tools.python.tool import PythonREPLTool
from . import utils


python_repl = PythonREPLTool(python_path=sys.executable)

@tool
def code_analysis(code: str) -> str:
    """Takes python code and gives back the output."""
    return python_repl.run(code)

@tool
def get_revenue_variance(start_month: str, end_month: str) -> float:
    """Calculate revenue variance (revenue vs budget) in USD over a date range."""
    return utils.revenue_variance(start_month, end_month)

@tool
def get_gross_margin_pct(start_month: str, end_month: str) -> float:
    """Calculate month on month gross margin percentage over a date range."""
    return utils.gross_margin_pct(start_month, end_month)

@tool
def get_opex_breakdown(start_month: str, end_month: str) -> dict:
    """Break down operating expenses by category in USD over a date range."""
    return utils.opex_breakdown(start_month, end_month)

@tool
def get_ebitda_proxy(start_month: str, end_month: str) -> float:
    """Calculate proxy EBITDA over a date range."""
    return utils.ebitda_proxy(start_month, end_month)

@tool
def get_cash_runway(as_of_month: str = None, last_n_months: int = 3) -> float:
    """Calculate cash runway in months based on historical or current burn rate."""
    return utils.cash_runway(as_of_month, last_n_months)

@tool
def plot_chart(chart_type: str, x: list, y: list, title: str, x_label: str, y_label: str, output_path: str = "chart.png", legends: list[str] | None = None) -> str:
    """Generate and save a graph/chart with the specified data and formatting."""
    return utils.plot_chart(chart_type, x, y, title, x_label, y_label, output_path, legends)


@st.cache_resource
def initialize_agent():
    """
    Initializes and returns the LangChain agent executor.
    This function is now self-contained and handles all agent logic.
    """

    try:
        gemini_client = ChatOpenAI(
            api_key=st.secrets["GOOGLE_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model="gemini-2.0-flash",
            temperature=0.2
        )
    except (KeyError, FileNotFoundError):
        st.error("GOOGLE_API_KEY not found. Please add it to your .streamlit/secrets.toml file.")
        st.stop()

    # --- Tool Definitions ---

    # --- System Prompt ---
    ma_prompt = ChatPromptTemplate.from_messages([
        ("system", """
    You are the Smart Financial Analytics Agent.

    You have access to data from an Excel file with these sheets:
    - actuals: (month, entity, account_category, amount, currency)
    - budget: (month, entity, account_category, amount, currency)
    - cash: (month, entity, cash_usd)
    - fx: (month, currency, rate_to_usd)

    Key points:
    - Always verify currencies. Default to USD; if EUR, convert using the fx sheet.
    - Months may appear as “YYYY-MM”, “June 2025”, “Jun’25”, etc. Treat them as equivalent.
    - account_category has values: Revenuem, COGS, Opex:Marketing, Opex:Sales, Opex:R&D, Opex:Admin

    Metric definitions:
    -Revenue (USD): actual vs budget.
    -Gross Margin %: (Revenue – COGS) / Revenue.
    -Opex total (USD): grouped by Opex:* categories.
    -EBITDA (proxy): Revenue – COGS – Opex.
    -Cash runway: cash ÷ avg monthly net burn (last 3 months).

    Dates:
    - Range 2023-01 to 2025-12
    - Normalize month formats into the same period.
    - If the user says "current year" or "this year", map it to the latest year in the dataset (2025).
    - If the user specifies a month without a year, default to the latest year available (2025).
    - If the request refers to a year outside the dataset range (2023–2025) or no matching data exists, ask the user for clarification.

    ONLY and ONLY follow this rule for user inquiries that cannot be served by an existing tool (e.g., parameter mismatch or unsupported operation):
    - Never respond with a denial.
    - Instead, write custom Python code that uses the code_analysis tool, load data.xlsx directly. Do not use custom or dummy data.
    - If your code errors, retry once with a corrected implementation.
    - If it still fails, deliver a concise, graceful explanation of the limitation and suggest a manual alternative.

    Instructions:
    1. If the user’s request matches a tool, call it. Sometime query needs to call more than one tool, you can call multiple tools multiple times if needed.
    2. Only call the 'code_analysis' tool as a last resort if no other tool is suitable.
    3. After a tool call:
       - Lead with the direct answer/figures.
       - Give a short interpretation (context, implications).
       - If a chart is generated, confirm that the chart is now displayed (put the chart path also in the response).
    4. Keep answers concise, actionable, and financially relevant, remember you are answer directly to the CFO of the company.
    """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    # --- Agent and Executor Creation ---
    tools = [code_analysis, get_cash_runway, get_ebitda_proxy, get_opex_breakdown, get_revenue_variance, get_gross_margin_pct, plot_chart]
    main_agent = create_openai_tools_agent(llm=gemini_client, tools=tools, prompt=ma_prompt)
    agent_executor = AgentExecutor(agent=main_agent, tools=tools, verbose=True, return_intermediate_steps=True)

    return agent_executor