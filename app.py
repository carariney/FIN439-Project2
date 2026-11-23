"""Streamlit committee interface. Run: streamlit run app.py."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from portfolio import BENCHMARK, ValidationError, apply_correlation_adjustment, compare_portfolios, estimate, load_prices

ROOT = Path(__file__).parent
ASSET_COLORS = {"BIL": "#168a8a", "IEF": "#4d7399", "AGG": "#7d91a8", "ACWI": "#173b5b"}


def percent(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value:.{digits}%}"


def render_kpi(label: str, value: str, caption: str) -> None:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-caption">{caption}</div></div>', unsafe_allow_html=True)


def render_stop(message: str) -> None:
    st.markdown(f'<div class="stop-banner"><span class="stop-label">STOP</span><span>{message}</span></div>', unsafe_allow_html=True)


def render_allocation_bar(label: str, weights: pd.Series) -> None:
    segments = "".join(f'<div class="allocation-segment" style="width:{weights[ticker] * 100:.4f}%;background:{ASSET_COLORS[ticker]}"></div>' for ticker in ASSET_COLORS if weights[ticker] > 0)
    legend = "".join(f'<span class="legend-item"><span class="legend-dot" style="background:{ASSET_COLORS[ticker]}"></span>{ticker} {weights[ticker]:.0%}</span>' for ticker in ASSET_COLORS)
    st.markdown(f'<div class="allocation-card"><div class="allocation-label">{label}</div><div class="allocation-bar">{segments}</div><div class="allocation-legend">{legend}</div></div>', unsafe_allow_html=True)


def display_verdicts(verdicts: pd.DataFrame) -> None:
    counts = verdicts["Verdict"].value_counts()
    chips = "".join(f'<span class="verdict-chip {verdict.lower().replace(" ", "-")}">{verdict}: {counts.get(verdict, 0)}</span>' for verdict in ("PASS", "FAIL", "NOT VERIFIED"))
    st.markdown(f'<div class="verdict-chips">{chips}</div>', unsafe_allow_html=True)
    rule_column, verdict_column, reason_column = st.columns([2.2, 1.15, 4.4])
    rule_column.markdown("**Rule**")
    verdict_column.markdown("**Verdict**")
    reason_column.markdown("**Reason**")
    for row in verdicts.itertuples(index=False):
        rule_column, verdict_column, reason_column = st.columns([2.2, 1.15, 4.4])
        rule_column.write(row.Rule)
        verdict_column.markdown(f'<span class="verdict-chip {row.Verdict.lower().replace(" ", "-")}">{row.Verdict}</span>', unsafe_allow_html=True)
        reason_column.write(row.Reason)


st.set_page_config(page_title="Meridian Foundation | Decision Lab", layout="wide")
st.markdown("""
<style>
  /* Native Streamlit theme colors are set in .streamlit/config.toml. */
  .block-container { max-width: 1280px; padding-top: 1.35rem; padding-bottom: 2rem; }
  h1, h2, h3 { color: #172c43; font-family: Georgia, "Times New Roman", serif; letter-spacing: -0.015em; }
  h1 { font-size: 2.05rem !important; margin-bottom: 0.05rem !important; }
  h2 { border-bottom: 1px solid #dce5ed; padding-bottom: 0.35rem; margin-top: 1.45rem !important; font-size: 1.3rem !important; }
  .decision-banner { background: #ffffff; border: 1px solid #dce5ed; border-left: 5px solid #0e817c; border-radius: 7px; padding: 0.8rem 1rem; margin: 0.7rem 0 0.9rem; box-shadow: 0 2px 5px rgba(23, 44, 67, 0.06); }
  .decision-title { color: #172c43; font-size: 1rem; font-weight: 700; }
  .decision-detail { color: #40566a; margin-top: 0.2rem; }
  .stop-banner { display: flex; align-items: baseline; gap: 0.55rem; background: #f7e9ea; border: 1px solid #ddbec2; border-left: 4px solid #8a3d47; border-radius: 6px; color: #57272e; padding: 0.7rem 0.85rem; margin: 0.55rem 0; line-height: 1.4; }
  .stop-label { color: #702b36; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.07em; }
  .kpi-card { background: #ffffff; border: 1px solid #dce5ed; border-radius: 8px; padding: 0.85rem 1rem; min-height: 110px; box-shadow: 0 2px 6px rgba(23, 44, 67, 0.07); }
  .kpi-label { color: #52697c; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
  .kpi-value { color: #172c43; font-size: 1.7rem; font-weight: 700; margin: 0.25rem 0; font-variant-numeric: tabular-nums; }
  .kpi-caption { color: #52697c; font-size: 0.76rem; line-height: 1.25; }
  .allocation-card { background: #ffffff; border: 1px solid #dce5ed; border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; box-shadow: 0 1px 3px rgba(23, 44, 67, 0.05); }
  .allocation-label { color: #172c43; font-weight: 700; margin-bottom: 0.5rem; }
  .allocation-bar { display: flex; overflow: hidden; height: 18px; border-radius: 4px; background: #e2eaf0; }
  .allocation-segment { min-width: 0; }
  .allocation-legend { display: flex; flex-wrap: wrap; gap: 0.85rem; margin-top: 0.55rem; color: #334e62; font-size: 0.8rem; font-variant-numeric: tabular-nums; }
  .legend-item { white-space: nowrap; }
  .legend-dot { display: inline-block; height: 9px; width: 9px; border-radius: 50%; margin-right: 0.3rem; }
  .verdict-chips { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 0.55rem; }
  .verdict-chip { border-radius: 999px; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.6rem; }
  .pass { background: #e0f0eb; color: #135e4d; }
  .fail { background: #f7e6e8; color: #7a2934; }
  .not-verified { background: #e4ebf0; color: #334e62; }
  [data-testid="stSidebar"] { background: #172c43; border-right: 1px solid #102338; min-width: 18rem !important; max-width: 18rem !important; }
  [data-testid="stSidebar"] > div:first-child { width: 18rem !important; }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label { color: #f7fafc; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  [data-testid="stSidebar"] h2 { border-bottom: 1px solid #496075; margin: 0 0 0.35rem !important; padding-bottom: 0.4rem; line-height: 1.25; }
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #c8d5df; }
  [data-testid="stSidebar"] input { color: #172c43 !important; background: #ffffff !important; }
  [data-testid="stSidebar"] [data-baseweb="select"] > div { background: #ffffff; border-color: #b9c8d4; color: #172c43; }
  [data-testid="stSidebar"] [data-baseweb="select"] * { color: #172c43; }
  [data-testid="stSidebar"] button { color: #172c43; }
  [data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] { background-color: #0e817c; }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.45rem; }
  @media (max-width: 720px) { h1 { font-size: 1.8rem !important; } .block-container { padding-left: 1rem; padding-right: 1rem; } }
</style>
""", unsafe_allow_html=True)

st.title("Meridian Foundation Portfolio Decision Lab")
st.caption("Investment-committee dashboard | constrained ETF allocation process")
st.warning("Historical estimates are not forecasts. A modeled PASS is not whole-mandate compliance.")

with st.sidebar:
    st.header("Scenario inputs")
    st.caption("All rates below are scenario assumptions. Percentages display as decimals in the model.")
    window = st.selectbox("Historical estimation window", [59, 36], format_func=lambda x: f"Last {x} monthly returns")
    inflation = st.number_input("Inflation assumption (%)", 0.0, 20.0, 2.5, 0.1) / 100
    target = st.number_input("Proxy return target (%)", 0.0, 30.0, 6.5, 0.1) / 100
    reserve = st.number_input("BIL reserve minimum (%)", 0.0, 100.0, 3.0, 0.5) / 100
    turnover_limit = st.number_input("Annual one-way turnover limit (%)", 0.0, 100.0, 25.0, 1.0) / 100
    cost_bps = st.number_input("Trading cost (bps one-way traded)", 0.0, 100.0, 10.0, 1.0)
    start_acwi = st.slider("Starting ACWI (%)", 0, 100, 60) / 100
    start_agg = 1 - start_acwi
    st.caption("Starting portfolio: 60% ACWI / 40% AGG; BIL and IEF start at 0%.")

st.markdown("""
<div class="decision-banner">
  <div class="decision-title">Committee decision: STOP — defer immediate adoption</div>
  <div class="decision-detail"><b>Authorized implementation allocation: 0% pending committee approval.</b> See allocation stability for the estimation-window evidence. A modeled feasible portfolio is not implementation approval.</div>
</div>
""", unsafe_allow_html=True)

try:
    prices = load_prices(ROOT / "prices.csv")
except ValidationError as exc:
    st.error(f"Decision blocked by data integrity: {exc}")
    st.markdown("The repository must contain the original, validated `prices.csv`; the app does not download or replace data. Date labels are period labels, not proof of publication/trade availability timestamps.")
    st.stop()

starting = pd.Series({"BIL": 0.0, "IEF": 0.0, "AGG": start_agg, "ACWI": start_acwi})
try:
    estimates = estimate(prices, window=window)
    with st.expander("Expected-return overrides (forecasts, not history)"):
        supplied = {ticker: st.number_input(f"{ticker} expected annual return (%)", -50.0, 50.0, float(estimates.mean[ticker] * 100), 0.1, key=ticker) / 100 for ticker in estimates.mean.index}
        use_override = st.checkbox("Use these expected-return assumptions in optimization")
    if use_override:
        estimates = estimate(prices, window=window, expected_returns=supplied)
    correlation_adjustment = st.sidebar.slider("ACWI–AGG correlation adjustment", -0.25, 0.25, 0.00, 0.01, help="Applied to each estimation window's own historical ACWI–AGG correlation. Invalid non-PSD covariance scenarios are rejected; they are never repaired.")
    estimates, historical_corr, correlation = apply_correlation_adjustment(estimates, "ACWI", "AGG", correlation_adjustment)
    result = compare_portfolios(estimates, target, reserve, starting, turnover_limit, cost_bps)
except ValidationError as exc:
    st.error(f"Scenario is infeasible or invalid: {exc}")
    st.stop()

constrained = result["Turnover-constrained minimum volatility"]
alternate_window = 36 if window == 59 else 59
alternate: dict | None = None
alternate_historical_corr: float | None = None
alternate_scenario_corr: float | None = None
sensitivity_error: str | None = None
if constrained["status"] != "INFEASIBLE":
    try:
        alternate_estimates = estimate(prices, window=alternate_window, expected_returns=supplied if use_override else None)
        alternate_estimates, alternate_historical_corr, alternate_scenario_corr = apply_correlation_adjustment(alternate_estimates, "ACWI", "AGG", correlation_adjustment)
        alternate = compare_portfolios(alternate_estimates, target, reserve, starting, turnover_limit, cost_bps)["Turnover-constrained minimum volatility"]
    except ValidationError as exc:
        sensitivity_error = str(exc)

st.subheader("Executive dashboard")
kpi_columns = st.columns(4)
if constrained["status"] == "INFEASIBLE":
    kpi_values = [("Gross annual return", "—", "Current constrained scenario is infeasible"), ("Annualized volatility", "—", "No feasible constrained allocation"), ("One-way turnover", "—", "No feasible constrained allocation")]
else:
    metrics, trade = constrained["metrics"], constrained["trade"]
    kpi_values = [("Gross annual return", percent(metrics["gross_annual_return"]), "Current modeled constrained portfolio"), ("Annualized volatility", percent(metrics["volatility"]), "Current modeled constrained portfolio"), ("One-way turnover", percent(trade["turnover"]), "From stated starting portfolio")]
for column, (label, value, caption) in zip(kpi_columns[:3], kpi_values):
    with column:
        render_kpi(label, value, caption)
with kpi_columns[3]:
    render_kpi("Authorized implementation", "0%", "Pending committee approval")

st.subheader("Allocation stability")
if constrained["status"] == "INFEASIBLE":
    render_stop("Turnover-constrained optimization is INFEASIBLE. Do not relax the return target or turnover limit automatically.")
elif sensitivity_error:
    render_stop(f"{alternate_window}-return correlation scenario unavailable. {sensitivity_error}")
elif alternate and alternate["status"] == "INFEASIBLE":
    render_stop(f"The {alternate_window}-return estimation window is INFEASIBLE. The process is unstable across reasonable windows.")
elif alternate:
    comparison_columns = st.columns(2)
    with comparison_columns[0]:
        render_allocation_bar(f"{window}-return constrained allocation", constrained["weights"])
    with comparison_columns[1]:
        render_allocation_bar(f"{alternate_window}-return sensitivity allocation", alternate["weights"])
    window_change = (constrained["weights"] - alternate["weights"]).abs().max()
    st.caption(f"ACWI–AGG correlation: {window}-return historical {historical_corr:.2f}, scenario {correlation:.2f}; {alternate_window}-return historical {alternate_historical_corr:.2f}, scenario {alternate_scenario_corr:.2f}.")
    if window_change >= .20 - 1e-12:
        render_stop(f"Estimation-window instability: largest allocation change is {window_change:.1%}, meeting or exceeding the 20.0% stopping threshold.")
    else:
        st.info(f"Largest allocation change across estimation windows: {window_change:.1%}; stopping threshold: 20.0%.")

st.subheader("Mandate and implementation boundary")
st.markdown("**Policy:** seven-year horizon; CPI + 4% net of costs over rolling five-year periods; 3% reserve; 60/40 ACWI/AGG reference benchmark; long-only/no borrowing, shorts, or derivatives; 8% nonexempt issuer cap; 25% annual turnover without approval; ≥90% five-business-day redeemability; calendar-year loss rule unresolved.")
st.markdown("**Implementation proposal pending CIO approval:** minimize estimated volatility subject to a proxy return threshold, reserve, long-only, and turnover constraints. BIL is the only reserve-eligible ETF; IEF is not labeled cash-equivalent.")
st.info(f"CPI + 4% is shown as {inflation:.1%} + 4.0% = {inflation + .04:.1%}; the separate modeled proxy threshold is {target:.1%}. Neither proves five-year, net-of-cost achievement.")

st.subheader("Portfolio comparison")
st.caption("Trading costs are one-time implementation costs. The five-year net return proxy spreads that one-time cost over five years for comparison only; it is not a recurring annual expense.")
status_labels = {"COMPARISON ONLY": "Comparison only", "EXCEEDS TURNOVER WITHOUT APPROVAL": "Turnover approval required", "FEASIBLE": "Modeled feasible, not approved", "INFEASIBLE": "Infeasible"}
summary = []
for name, item in result.items():
    if item["status"] == "INFEASIBLE":
        summary.append({"Portfolio": name, "Status": status_labels[item["status"]], "Reason": item["reason"]})
        continue
    metrics, trade = item["metrics"], item["trade"]
    summary.append({"Portfolio": name, "Status": status_labels[item["status"]], "Gross return": metrics["gross_annual_return"], "5-year net proxy": metrics["five_year_net_return_proxy"], "Volatility": metrics["volatility"], "Reserve": metrics["reserve"], "Turnover": trade["turnover"], "One-time cost": trade["cost"]})
summary_frame = pd.DataFrame(summary).set_index("Portfolio")
numeric_columns = ["Gross return", "5-year net proxy", "Volatility", "Reserve", "Turnover", "One-time cost"]
display_columns = [column for column in numeric_columns if column in summary_frame.columns]
st.caption("Approval status")
st.dataframe(summary_frame[["Status"]], column_config={"Status": st.column_config.TextColumn(width="large")}, use_container_width=True)
if display_columns:
    metric_display = summary_frame[display_columns].map(lambda value: f"{value:.2%}" if pd.notna(value) else "—").reset_index()
    metric_config = {"Portfolio": st.column_config.TextColumn(width="medium")}
    metric_config.update({column: st.column_config.TextColumn(width="small") for column in display_columns})
    st.dataframe(metric_display, column_config=metric_config, hide_index=True, use_container_width=True)
else:
    st.caption("Financial metrics are unavailable for infeasible portfolios.")
if "Reason" in summary_frame.columns and summary_frame["Reason"].notna().any():
    with st.expander("Approval-context notes", expanded=False):
        st.dataframe(summary_frame[["Reason"]].dropna(), use_container_width=True)
st.caption("“Modeled feasible” means the coded scenario constraints are met; it does not establish whole-mandate compliance or implementation approval.")

st.subheader("Mandate transparency")
st.info("Outstanding evidence before approval: issuer look-through/exemptions, five-business-day redeemability, ETF derivative exposure, the CIO's calendar-loss definition, and demonstrated rolling five-year CPI + 4% net performance.")
mandate_summary = []
for name, item in result.items():
    if item["status"] == "INFEASIBLE":
        mandate_summary.append({"Portfolio": name, "PASS": "—", "FAIL": "—", "NOT VERIFIED": "—"})
        continue
    counts = item["verdicts"]["Verdict"].value_counts()
    mandate_summary.append({"Portfolio": name, "PASS": str(counts.get("PASS", 0)), "FAIL": str(counts.get("FAIL", 0)), "NOT VERIFIED": str(counts.get("NOT VERIFIED", 0))})
st.caption("Mandate-test summary")
# All cells are presentation values.  Keep the frame string-typed so Arrow does
# not need to reconcile count integers with infeasibility placeholders.
mandate_summary_display = pd.DataFrame(mandate_summary, dtype="string").set_index("Portfolio")
st.dataframe(mandate_summary_display, use_container_width=True)
for name, item in result.items():
    with st.expander(name, expanded=name == "Turnover-constrained minimum volatility"):
        if item["status"] == "INFEASIBLE":
            st.error(item["reason"])
            continue
        st.write("Weights")
        weight_column, _ = st.columns([1.6, 3.4])
        with weight_column:
            st.dataframe((item["weights"] * 100).rename("Weight %").to_frame().style.format("{:.1f}%"), height=180, use_container_width=True)
        st.write("Mandate tests")
        display_verdicts(item["verdicts"])

st.subheader("Point-in-time monitoring signal")
lookback = st.slider("Trailing-return lookback (months)", 3, 24, 12)
asof = st.date_input("Decision-date cutoff", value=date.fromisoformat(str(prices.index.max())), min_value=date.fromisoformat(str(prices.index.min())), max_value=date.fromisoformat(str(prices.index.max())))
eligible = prices.loc[prices.index <= asof.isoformat()]
if len(eligible) > lookback:
    signals = eligible.iloc[-1] / eligible.iloc[-lookback - 1] - 1
    st.dataframe(signals.rename(f"{lookback}-month trailing return").to_frame().style.format("{:.2%}"), use_container_width=True)
else:
    st.warning("Insufficient eligible monthly observations for the selected signal lookback.")
st.caption("Data card: source is the bundled validated CSV; observation period uses monthly period labels through the cutoff; calculation is last price / price N months earlier − 1; no transformations other than returns; missing data stops the app. Yahoo adjusted-price publication timestamps are not present, so labels do not prove availability. The signal is a monitoring input, not an automatic trade.")

st.subheader("Committee guardrail")
if constrained["status"] == "INFEASIBLE":
    render_stop("Turnover-constrained optimization is INFEASIBLE. Do not relax the return target or turnover limit automatically.")
elif sensitivity_error:
    render_stop(f"{alternate_window}-return correlation scenario unavailable. {sensitivity_error}")
elif alternate and alternate["status"] == "INFEASIBLE":
    render_stop(f"The {alternate_window}-return estimation window is INFEASIBLE. The process is unstable across reasonable windows.")
elif alternate:
    failure = constrained["verdicts"].query("Verdict == 'FAIL'")
    largest_change = (constrained["weights"] - starting).abs().max()
    window_change = (constrained["weights"] - alternate["weights"]).abs().max()
    st.write(f"Estimation-window sensitivity: largest turnover-constrained allocation change between {window} and {alternate_window} returns is {window_change:.1%}.")
    st.caption(f"Separate transition diagnostic: largest allocation change from the stated starting portfolio is {largest_change:.1%}.")
    if window_change >= .20 - 1e-12:
        render_stop(f"Guardrail active: the {window_change:.1%} estimation-window allocation change meets or exceeds the 20.0% stopping threshold. Do not adopt automatically.")
    elif len(failure):
        render_stop(f"Modeled hard-mandate failure: {len(failure)} rule failure(s) require escalation.")
    elif largest_change > .25:
        render_stop(f"Initial allocation change is {largest_change:.1%}, above the 25.0% transition diagnostic.")
    else:
        st.warning("PILOT ONLY: modeled constraints pass, but material policy rules remain NOT VERIFIED. Committee action is still required.")
