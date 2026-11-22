"""Streamlit committee interface. Run: streamlit run app.py"""
from __future__ import annotations
from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st
from portfolio import BENCHMARK, ValidationError, load_prices, estimate, compare_portfolios, apply_correlation_adjustment
from asof import trailing_signals

ROOT = Path(__file__).parent
st.set_page_config(page_title="Meridian Foundation | Decision Lab", layout="wide")
st.title("Meridian Foundation Portfolio Decision Lab")
st.caption("Decision question: adopt, pilot, or reject a constrained minimum-volatility ETF process?")
st.warning("Historical estimates are not forecasts. A PASS on a modeled check is not whole-mandate compliance.")

with st.sidebar:
    st.header("Scenario inputs")
    window = st.selectbox("Historical estimation window", [59, 36], format_func=lambda x: f"Last {x} monthly returns")
    inflation = st.number_input("Inflation assumption (%)", 0.0, 20.0, 2.5, 0.1) / 100
    target = st.number_input("Proxy return target (%)", 0.0, 30.0, 6.5, 0.1) / 100
    reserve = st.number_input("BIL reserve minimum (%)", 0.0, 100.0, 3.0, 0.5) / 100
    turnover_limit = st.number_input("Annual one-way turnover limit (%)", 0.0, 100.0, 25.0, 1.0) / 100
    cost_bps = st.number_input("Trading cost (bps one-way traded)", 0.0, 100.0, 10.0, 1.0)
    st.caption("Starting portfolio (default: 60% ACWI / 40% AGG)")
    start_acwi = st.slider("Starting ACWI (%)", 0, 100, 60) / 100
    start_agg = 1 - start_acwi
    st.caption("IEF and BIL starting weights are 0%; this is an explicit simplified starting convention.")

st.subheader("Mandate and implementation boundary")
st.markdown("**Policy:** seven-year horizon; CPI + 4% net of costs over rolling five-year periods; 3% reserve; 60/40 ACWI/AGG reference benchmark; long-only/no borrowing, shorts, or derivatives; 8% nonexempt issuer cap; 25% annual turnover without approval; ≥90% five-business-day redeemability; calendar-year loss rule unresolved.  \\n**Implementation proposal pending CIO approval:** minimize estimated volatility subject to a proxy return threshold, reserve, long-only, and turnover constraints. BIL is the only reserve-eligible ETF; IEF is not labeled cash-equivalent.")
st.info(f"CPI + 4% is shown as {inflation:.1%} + 4.0% = {inflation + .04:.1%}; the separate modeled proxy threshold is {target:.1%}. Neither proves five-year, net-of-cost achievement.")

try:
    prices = load_prices(ROOT / "prices.csv")
except ValidationError as exc:
    st.error(f"Decision blocked by data integrity: {exc}")
    st.markdown("The repository must contain the original, validated `prices.csv`; the app does not download or replace data. Date labels are period labels, not proof of publication/trade availability timestamps.")
    st.stop()

starting = pd.Series({"BIL": 0.0, "IEF": 0.0, "AGG": start_agg, "ACWI": start_acwi})
try:
    estimates = estimate(prices, window=window)
    # Users may override the estimates only after seeing historical estimates; inputs remain decimal internally.
    with st.expander("Expected-return overrides (forecasts, not history)"):
        supplied = {ticker: st.number_input(f"{ticker} expected annual return (%)", -50.0, 50.0, float(estimates.mean[ticker] * 100), 0.1, key=ticker) / 100 for ticker in estimates.mean.index}
        use_override = st.checkbox("Use these expected-return assumptions in optimization")
    if use_override: estimates = estimate(prices, window=window, expected_returns=supplied)
    correlation_adjustment = st.sidebar.slider("ACWI–AGG correlation adjustment", -0.25, 0.25, 0.00, 0.01, help="Applied to each estimation window's own historical ACWI–AGG correlation. Invalid non-PSD covariance scenarios are rejected; they are never repaired.")
    estimates, historical_corr, correlation = apply_correlation_adjustment(estimates, "ACWI", "AGG", correlation_adjustment)
    st.caption(f"Current-window ACWI–AGG correlation: historical {historical_corr:.2f}; scenario {correlation:.2f} (adjustment {correlation_adjustment:+.2f}).")
    result = compare_portfolios(estimates, target, reserve, starting, turnover_limit, cost_bps)
except ValidationError as exc:
    st.error(f"Scenario is infeasible or invalid: {exc}")
    st.stop()

st.subheader("Comparison")
st.caption("Trading costs are one-time implementation costs. ‘Five-year net return proxy’ spreads that one-time cost over five years for comparison only; it is not a recurring annual expense.")
summary = []
for name, item in result.items():
    if item["status"] == "INFEASIBLE":
        summary.append({"Portfolio": name, "Status": "INFEASIBLE", "Reason": item["reason"]})
        continue
    m, trade = item["metrics"], item["trade"]
    summary.append({"Portfolio": name, "Status": item["status"], "Gross annual return": m["gross_annual_return"], "Five-year net return proxy": m["five_year_net_return_proxy"], "Est. annual volatility": m["volatility"], "BIL reserve": m["reserve"], "Return vs benchmark": item["benchmark_relative"]["return"], "Volatility vs benchmark": item["benchmark_relative"]["volatility"], "One-way turnover": trade["turnover"], "Est. one-time cost": trade["cost"]})
st.dataframe(pd.DataFrame(summary).set_index("Portfolio").style.format({column: "{:.2%}" for column in ["Gross annual return", "Five-year net return proxy", "Est. annual volatility", "BIL reserve", "Return vs benchmark", "Volatility vs benchmark", "One-way turnover", "Est. one-time cost"]}), use_container_width=True)

for name, item in result.items():
    with st.expander(name, expanded=name == "Turnover-constrained minimum volatility"):
        if item["status"] == "INFEASIBLE":
            st.error(item["reason"])
            continue
        st.write("Weights")
        st.dataframe((item["weights"] * 100).rename("Weight %").to_frame().style.format("{:.1f}%"))
        st.write("Mandate tests")
        st.dataframe(item["verdicts"], use_container_width=True)

st.subheader("Point-in-time monitoring signal")
lookback = st.slider("Trailing-return lookback (months)", 3, 24, 12)
asof = st.date_input("Decision-date cutoff", value=date.fromisoformat(str(prices.index.max())), min_value=date.fromisoformat(str(prices.index.min())), max_value=date.fromisoformat(str(prices.index.max())))
eligible = prices.loc[prices.index <= asof.isoformat()]
if len(eligible) > lookback:
    signal_rows = pd.DataFrame({"ticker": eligible.columns, "observation_date": eligible.index[-1], "value": eligible.iloc[-1].values})
    signals = eligible.iloc[-1] / eligible.iloc[-lookback - 1] - 1
    st.dataframe(signals.rename(f"{lookback}-month trailing return").to_frame().style.format("{:.2%}"))
else: st.warning("Insufficient eligible monthly observations for the selected signal lookback.")
st.caption("Data card: source is the bundled validated CSV; observation period uses monthly period labels through the cutoff; calculation is last price / price N months ago − 1; no transformations other than returns; missing data stops the app. Yahoo adjusted-price publication timestamps are not present, so labels do not prove availability. The signal is a monitoring input, not an automatic trade.")

constrained = result["Turnover-constrained minimum volatility"]
st.subheader("Committee guardrail")
if constrained["status"] == "INFEASIBLE":
    st.error("STOP: turnover-constrained optimization is INFEASIBLE. Do not relax the return target or turnover limit automatically.")
else:
    failure = constrained["verdicts"].query("Verdict == 'FAIL'")
    largest_change = (constrained["weights"] - starting).abs().max()
    alternate_window = 36 if window == 59 else 59
    try:
        alternate_estimates = estimate(prices, window=alternate_window, expected_returns=supplied if use_override else None)
        alternate_estimates, alternate_historical_corr, alternate_scenario_corr = apply_correlation_adjustment(alternate_estimates, "ACWI", "AGG", correlation_adjustment)
        alternate = compare_portfolios(alternate_estimates, target, reserve, starting, turnover_limit, cost_bps)["Turnover-constrained minimum volatility"]
        st.caption(f"{alternate_window}-return ACWI–AGG correlation: historical {alternate_historical_corr:.2f}; scenario {alternate_scenario_corr:.2f} (same adjustment {correlation_adjustment:+.2f}).")
        if alternate["status"] == "INFEASIBLE":
            st.error(f"STOP: the {alternate_window}-return estimation window is INFEASIBLE; process is unstable across reasonable windows.")
        else:
            window_change = (constrained["weights"] - alternate["weights"]).abs().max()
            st.write(f"Window sensitivity: largest turnover-constrained allocation change between {window} and {alternate_window} returns is {window_change:.1%}.")
            if len(failure) or largest_change > .25 or window_change >= .20 - 1e-12:
                st.error(f"SUSPEND / escalate: {len(failure)} modeled rule failure(s), largest initial allocation change {largest_change:.1%}, or window-instability threshold breached. Do not adopt automatically.")
            else:
                st.warning("PILOT ONLY: modeled constraints pass, but material policy rules remain NOT VERIFIED. Committee action is still required.")
    except ValidationError as exc:
        st.error(f"STOP: {alternate_window}-return correlation scenario unavailable: {exc}")
