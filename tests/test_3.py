# tests/test_agent_tool_selection_by_log.py
import pytest
from agent.agent import initialize_agent
from unittest.mock import patch, Mock

@pytest.fixture(autouse=True)
def agent_executor():
    # Create an agent with a dummy LLM but real logging of tool calls
    with patch("streamlit.secrets", {"GOOGLE_API_KEY": "AIzaSyBxrJAxe69t02jMZKtOGXY3gCIgVm8RAMY"}):
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            mock_llm.return_value = Mock()
            yield initialize_agent()

@pytest.mark.parametrize("query,tool_name", [
    ("What is revenue variance for January 2025?", "get_revenue_variance"),
    ("What is our cash runway for 2025?",        "get_cash_runway"),
    ("Show me gross margin percentage for July 2025", "get_gross_margin_pct"),
    ("Break down opex by category for 2025",     "get_opex_breakdown"),
    ("What's our EBITDA right now for last 3 months?", "get_ebitda_proxy"),
])
def test_tool_selected_in_logs(agent_executor, capsys, query, tool_name):
    # Run the agent; it will print "Invoking: `tool_name` with ..."
    agent_executor({"input": query})
    captured = capsys.readouterr().out
    assert f"Invoking: `{tool_name}`" in captured
