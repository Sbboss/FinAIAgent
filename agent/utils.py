import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load and prepare data
dfs = pd.read_excel("data.xlsx", sheet_name=None)
actuals = dfs["actuals"].copy()
budget = dfs["budget"].copy()
cash = dfs["cash"].copy()
fx = dfs["fx"].copy()

# Normalize month columns
for df in (actuals, budget, cash, fx):
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M")

# Helper: convert any DataFrame with `amount` & `currency` to USD
def convert_to_usd(df: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    merged = df.merge(
        fx,
        on=["month", "currency"],
        how="left",
        suffixes=("", "_fx"),
    )
    merged["rate_to_usd"] = merged["rate_to_usd"].fillna(1.0)
    merged["amount_usd"] = merged["amount"] * merged["rate_to_usd"]
    return merged

# 1. Revenue variance
def revenue_variance(start_month: str, end_month: str) -> float:
    a = convert_to_usd(actuals, fx)
    b = convert_to_usd(budget, fx)
    mask = lambda df: (df["month"] >= pd.Period(start_month)) & (df["month"] <= pd.Period(end_month))
    actual_rev = a[mask(a) & (a["account_category"] == "Revenue")]["amount_usd"].sum()
    budget_rev = b[mask(b) & (b["account_category"] == "Revenue")]["amount_usd"].sum()
    return actual_rev - budget_rev, actual_rev, budget_rev

# 2. Gross Margin %
def gross_margin_pct(start_month: str, end_month: str) -> float:
    a = convert_to_usd(actuals, fx)
    mask = (a["month"] >= pd.Period(start_month)) & (a["month"] <= pd.Period(end_month))

    result = {}
    for m in sorted(a[mask]["month"].unique()):
        sub = a[a["month"] == m]
        rev = sub[sub["account_category"] == "Revenue"]["amount_usd"].sum()
        cogs = sub[sub["account_category"] == "COGS"]["amount_usd"].sum()
        result[str(m)] = round((rev - cogs) / rev * 100, 2) if rev != 0 else 0.0

    return result

# 3. Opex breakdown
def opex_breakdown(start_month: str, end_month: str) -> dict:
    a = convert_to_usd(actuals, fx)
    mask = (a["month"] >= pd.Period(start_month)) & (a["month"] <= pd.Period(end_month))
    opex = a[mask & a["account_category"].str.startswith("Opex")]
    return opex.groupby("account_category")["amount_usd"].sum().to_dict()

# 4. EBITDA proxy
def ebitda_proxy(start_month: str, end_month: str) -> float:
    a = convert_to_usd(actuals, fx)
    mask = (a["month"] >= pd.Period(start_month)) & (a["month"] <= pd.Period(end_month))
    rev = a[mask & (a["account_category"] == "Revenue")]["amount_usd"].sum()
    cogs = a[mask & (a["account_category"] == "COGS")]["amount_usd"].sum()
    opex = a[mask & a["account_category"].str.startswith("Opex")]["amount_usd"].sum()
    return rev - cogs - opex

# 5. Cash runway
def cash_runway(as_of_month: str = None, last_n_months: int = 3) -> float:
    # If no as_of_month specified, use most recent
    if as_of_month is None:
        most_recent = cash["month"].max()
    else:
        most_recent = pd.Period(as_of_month)

    # Get cash balance as of the specified/most recent month
    cash_usd = cash[cash["month"] == most_recent]["cash_usd"].sum()

    # Calculate net burn for each of the last N months before as_of_month
    a = convert_to_usd(actuals, fx)

    # Get months ending before as_of_month
    available_months = sorted([m for m in a["month"].unique() if m < most_recent])
    months = available_months[-last_n_months:] if len(available_months) >= last_n_months else available_months

    burns = []
    for m in months:
        dfm = a[a["month"] == m]
        rev = dfm[dfm["account_category"] == "Revenue"]["amount_usd"].sum()
        cogs = dfm[dfm["account_category"] == "COGS"]["amount_usd"].sum()
        opex = dfm[dfm["account_category"].str.startswith("Opex")]["amount_usd"].sum()
        burns.append(cogs + opex - rev)

    avg_burn = sum(burns) / len(burns) if burns else 0
    return cash_usd / avg_burn if avg_burn > 0 else float('inf'), avg_burn

def plot_chart(
    chart_type: str,
    x,
    y,
    title: str,
    x_label: str,
    y_label: str,
    output_path: str,
    legends: list[str] | None = None,   # ← NEW
) -> str:
    """
            Plot helper that supports single-series and multi-series
            bar, line, scatter and pie charts.

            Parameters
            ----------
            chart_type : {"bar", "line", "scatter", "pie"}
            x, y       : list-like objects.  For multi-series data,
                         use y = [[series1], [series2], …] and
                         x  = [[categories]].
            legends    : Optional list of legend labels, one per series.
            """
    try:

        plt.figure(figsize=(7, 4))

        # ── MULTI-SERIES ────────────────────────────────────────────────
        if isinstance(y[0], list) and len(y) > 1:
            categories = x[0]  # shared x-axis
            n_groups = len(categories)
            n_series = len(y)

            if chart_type == "bar":
                bar_width = 0.8 / n_series
                x_pos = np.arange(n_groups)
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c',
                          '#d62728', '#9467bd']

                for i, series in enumerate(y):
                    offset = (i - n_series / 2 + 0.5) * bar_width
                    plt.bar(
                        x_pos + offset,
                        series,
                        bar_width,
                        color=colors[i % len(colors)],
                        label=(legends[i] if legends and i < len(legends)
                               else f"Series {i + 1}")
                    )

                plt.xticks(x_pos, categories, rotation=45)
                plt.legend()

            elif chart_type == "line":
                for i, series in enumerate(y):
                    plt.plot(
                        categories,
                        series,
                        marker="o",
                        label=(legends[i] if legends and i < len(legends)
                               else f"Series {i + 1}")
                    )
                plt.legend()
                plt.xticks(rotation=45)

        # ── SINGLE-SERIES ───────────────────────────────────────────────
        else:
            # flatten if wrapped
            if isinstance(y[0], list): y = y[0]
            if isinstance(x[0], list): x = x[0]

            if chart_type == "line":
                plt.plot(x, y, marker="o", linewidth=2, markersize=6,
                         label=legends[0] if legends else None)
            elif chart_type == "bar":
                plt.bar(x, y, color="skyblue", edgecolor="navy", alpha=0.7,
                        label=legends[0] if legends else None)
                plt.xticks(rotation=45)
                plt.ylim(bottom=0)
            elif chart_type == "scatter":
                plt.scatter(x, y, s=60, alpha=0.7,
                            label=legends[0] if legends else None)
            elif chart_type == "pie":
                plt.pie(y, labels=x, autopct="%1.1f%%", startangle=90)
                plt.axis("equal")

            if legends and chart_type != "pie":
                plt.legend()

        # ── COMMON FORMATTING ──────────────────────────────────────────
        plt.title(title, fontsize=14, fontweight="bold")

        if chart_type != "pie":
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches="tight")
        plt.close()
        return output_path

    except Exception as e:
        return f'There is some problem with the data you send, I am using matplotlib to plot. Can you send a full code to other tool which could run on PythonREPLTool (should save the graph and return the filename). Here is the error: {e}'
        # return f'There is some problem with the data you send, I am using matplotlib to plot. Can you recheck the data and send it again. May be just include the most important field to plot. Here is the error: {e}'