# test_module_level_tools.py
import pytest
from unittest.mock import patch, Mock
from agent import agent
from agent.agent import (
    code_analysis,
    get_revenue_variance,
    get_gross_margin_pct,
    get_opex_breakdown,
    get_ebitda_proxy,
    get_cash_runway,
    plot_chart
)


class TestModuleLevelTools:
    """Test the module-level tool definitions"""

    def test_tools_have_correct_decorators(self):
        """Test that all tools are properly decorated"""
        tools = [
            code_analysis,
            get_revenue_variance,
            get_gross_margin_pct,
            get_opex_breakdown,
            get_ebitda_proxy,
            get_cash_runway,
            plot_chart
        ]

        for tool in tools:
            # Check that tool has required attributes from @tool decorator
            assert hasattr(tool, 'name'), f"Tool {tool} missing 'name' attribute"
            assert hasattr(tool, 'description'), f"Tool {tool} missing 'description' attribute"
            assert hasattr(tool, 'args_schema'), f"Tool {tool} missing 'args_schema' attribute"

    def test_tool_names_are_correct(self):
        """Test that tool names match function names"""
        expected_names = {
            'code_analysis': code_analysis.name,
            'get_revenue_variance': get_revenue_variance.name,
            'get_gross_margin_pct': get_gross_margin_pct.name,
            'get_opex_breakdown': get_opex_breakdown.name,
            'get_ebitda_proxy': get_ebitda_proxy.name,
            'get_cash_runway': get_cash_runway.name,
            'plot_chart': plot_chart.name,
        }

        for expected_name, actual_name in expected_names.items():
            assert expected_name == actual_name

    def test_tool_descriptions_exist(self):
        """Test that all tools have non-empty descriptions"""
        tools = [code_analysis, get_revenue_variance, get_gross_margin_pct,
                 get_opex_breakdown, get_ebitda_proxy, get_cash_runway, plot_chart]

        for tool in tools:
            assert tool.description is not None
            assert len(tool.description.strip()) > 0

    @patch('agent.utils.revenue_variance')
    def test_get_revenue_variance_tool_execution(self, mock_utils_func):
        """Test revenue variance tool execution"""
        mock_utils_func.return_value = 5000.0

        result = get_revenue_variance.invoke({
            'start_month': '2025-01',
            'end_month': '2025-01'
        })

        assert result == 5000.0
        mock_utils_func.assert_called_once_with('2025-01', '2025-01')

    @patch('agent.utils.cash_runway')
    def test_get_cash_runway_tool_execution(self, mock_utils_func):
        """Test cash runway tool with optional parameters"""
        mock_utils_func.return_value = 12.5

        # Test with default parameters
        result = get_cash_runway.invoke({})
        assert result == 12.5
        mock_utils_func.assert_called_once_with(None, 3)

        # Test with custom parameters
        mock_utils_func.reset_mock()
        result = get_cash_runway.invoke({
            'as_of_month': '2025-01',
            'last_n_months': 6
        })
        assert result == 12.5
        mock_utils_func.assert_called_once_with('2025-01', 6)

    def test_python_repl_tool_instance(self):
        """Test that python_repl is properly initialized"""
        assert agent.python_repl is not None
        assert hasattr(agent.python_repl, 'run')

    @patch('agent.agent.python_repl')
    def test_code_analysis_tool_execution(self, mock_python_repl):
        """Test code analysis tool execution"""
        mock_python_repl.run.return_value = "Output: 42"

        result = code_analysis.invoke({'code': 'print(21 * 2)'})

        assert result == "Output: 42"
        mock_python_repl.run.assert_called_once_with('print(21 * 2)')
