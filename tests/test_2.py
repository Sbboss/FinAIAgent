# tests/test_agent_tool_selection_updated.py
import pytest
from unittest.mock import patch, Mock
from agent.agent import initialize_agent
from langchain.agents.agent import AgentExecutor

class TestAgentToolSelectionUpdated:

    @pytest.fixture(autouse=True)
    def setup_agent(self):
        with patch("streamlit.secrets", {"GOOGLE_API_KEY": "AIzaSyBxrJAxe69t02jMZKtOGXY3gCIgVm8RAMY"}):
            with patch("langchain_openai.ChatOpenAI") as mock_llm:
                mock_llm.return_value = Mock()
                self.agent = initialize_agent()

    def test_agent_has_all_tools_registered(self):
        expected = {
            "code_analysis",
            "get_revenue_variance",
            "get_gross_margin_pct",
            "get_opex_breakdown",
            "get_ebitda_proxy",
            "get_cash_runway",
            "plot_chart"
        }
        actual = {tool.name for tool in self.agent.tools}
        assert expected == actual
