"""Auditable portfolio calculations for the Meridian Foundation decision lab.

All weights and rates are decimals internally (0.03 means 3%).  This module does
not download data: the decision boundary is the bundled CSV supplied by the user.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd

TICKERS = ("BIL", "IEF", "AGG", "ACWI")
EXPECTED_PERIODS = pd.period_range("2021-10", "2026-09", freq="M")
BENCHMARK = pd.Series({"BIL": 0.0, "IEF": 0.0, "AGG": 0.40, "ACWI": 0.60})
RESERVE_ELIGIBLE = {"BIL"}


class ValidationError(ValueError):
    """Input has failed an explicit model validation."""


@dataclass(frozen=True)
class Estimates:
    mean: pd.Series
    covariance: pd.DataFrame
    returns: pd.DataFrame


def _as_series(weights: pd.Series | dict[str, float]) -> pd.Series:
    result = pd.Series(weights, dtype=float).reindex(TICKERS)
    if result.isna().any():
        raise ValidationError("Weights must supply exactly BIL, IEF, AGG, and ACWI.")
    if not np.isfinite(result.to_numpy()).all():
        raise ValidationError("Weights must be finite decimal values.")
    return result


def validate_weights(weights: pd.Series | dict[str, float]) -> pd.Series:
    result = _as_series(weights)
    if (result < -1e-12).any():
        raise ValidationError("Long-only portfolios cannot have negative weights.")
    if not np.isclose(result.sum(), 1.0, atol=1e-9):
        raise ValidationError(f"Weights must sum to 100%; received {result.sum():.6%}.")
    return result


def validate_covariance(covariance: pd.DataFrame | np.ndarray) -> np.ndarray:
    array = np.asarray(covariance, dtype=float)
    if array.shape != (len(TICKERS), len(TICKERS)):
        raise ValidationError("Covariance matrix must be 4 by 4 in ticker order.")
    if not np.isfinite(array).all():
        raise ValidationError("Covariance matrix contains invalid values.")
    if not np.allclose(array, array.T, atol=1e-10):
        raise ValidationError("Covariance matrix must be symmetric.")
    if np.linalg.eigvalsh(array).min() < -1e-10:
        raise ValidationError("Covariance matrix must be positive semidefinite.")
    return array


def load_prices(path: str | Path = "prices.csv") -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise ValidationError(
            f"Bundled price file not found: {path}. Do not substitute fetched prices; restore the original CSV."
        )
    frame = pd.read_csv(path)
    expected_columns = ["Date", *TICKERS]
    if list(frame.columns) != expected_columns:
        raise ValidationError(f"Expected columns {expected_columns}; received {list(frame.columns)}.")
    if frame.isna().any().any():
        raise ValidationError("prices.csv has missing cells; analysis stopped.")
    parsed_dates: list[date] = []
    try:
        parsed_dates = [date.fromisoformat(str(value)) for value in frame["Date"]]
    except (TypeError, ValueError):
        raise ValidationError("prices.csv contains an invalid Date.")
    periods = [f"{value.year:04d}-{value.month:02d}" for value in parsed_dates]
    if len(set(periods)) != len(periods) or periods != sorted(periods):
        raise ValidationError("Monthly dates must be unique and chronological.")
    expected = [str(value) for value in EXPECTED_PERIODS]
    missing = sorted(set(expected).difference(periods))
    extra = sorted(set(periods).difference(expected))
    if len(frame) != 60 or len(missing) or len(extra):
        details = []
        if len(missing): details.append("missing " + ", ".join(str(x) for x in missing))
        if len(extra): details.append("unexpected " + ", ".join(str(x) for x in extra))
        raise ValidationError("Expected 60 monthly labels Oct-2021 through Sep-2026; " + "; ".join(details))
    values = frame.loc[:, TICKERS].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all() or (values <= 0).any().any():
        raise ValidationError("All ETF prices must be finite, numeric, and strictly positive.")
    out = values.copy()
    # Preserve ISO period labels as plain strings: the model needs ordering, not
    # unverified intraday timestamps, and this avoids fragile native conversions.
    out.index = pd.Index(frame["Date"].astype(str), dtype=object)
    out.index.name = "Date"
    return out


def monthly_returns(prices: pd.DataFrame) -> pd.DataFrame:
    returns = prices.pct_change().iloc[1:]
    if returns.isna().any().any() or not np.isfinite(returns.to_numpy()).all():
        raise ValidationError("Could not calculate finite monthly returns.")
    return returns


def estimate(prices: pd.DataFrame, window: int = 59, expected_returns: dict[str, float] | None = None) -> Estimates:
    returns = monthly_returns(prices)
    if window not in (36, 59) or len(returns) < window:
        raise ValidationError("Estimation window must be 36 or 59 available monthly returns.")
    sample = returns.tail(window)
    covariance = sample.cov() * 12
    validate_covariance(covariance.loc[TICKERS, TICKERS])
    mean = sample.mean() * 12  # arithmetic annualization; estimate, not a forecast
    if expected_returns is not None:
        supplied = _as_series(expected_returns)
        mean = supplied
    return Estimates(mean=mean, covariance=covariance, returns=sample)


def stress_pair_correlation(estimates: Estimates, ticker_a: str, ticker_b: str, correlation: float) -> Estimates:
    """Replace one pairwise correlation while retaining all asset volatilities.

    This is an explicit scenario assumption, not a forecast.  The resulting
    covariance matrix must remain positive semidefinite or the scenario is
    rejected rather than repaired.
    """
    if ticker_a not in TICKERS or ticker_b not in TICKERS or ticker_a == ticker_b:
        raise ValidationError("Correlation stress requires two distinct universe tickers.")
    if not np.isfinite(correlation) or not -1 <= correlation <= 1:
        raise ValidationError("Correlation assumption must be between -1 and 1.")
    covariance = estimates.covariance.loc[TICKERS, TICKERS].copy()
    vol = np.sqrt(np.diag(validate_covariance(covariance)))
    value = correlation * vol[TICKERS.index(ticker_a)] * vol[TICKERS.index(ticker_b)]
    covariance.loc[ticker_a, ticker_b] = value
    covariance.loc[ticker_b, ticker_a] = value
    validate_covariance(covariance)
    return Estimates(mean=estimates.mean.copy(), covariance=covariance, returns=estimates.returns.copy())


def pair_correlation(estimates: Estimates, ticker_a: str, ticker_b: str) -> float:
    covariance = estimates.covariance.loc[TICKERS, TICKERS]
    denominator = np.sqrt(covariance.loc[ticker_a, ticker_a] * covariance.loc[ticker_b, ticker_b])
    if denominator <= 0:
        raise ValidationError("Cannot calculate correlation for an asset with zero volatility.")
    return float(covariance.loc[ticker_a, ticker_b] / denominator)


def apply_correlation_adjustment(estimates: Estimates, ticker_a: str, ticker_b: str, adjustment: float) -> tuple[Estimates, float, float]:
    """Apply the same correlation adjustment to each window's own baseline.

    Returns the stressed estimates, that window's historical correlation, and
    the scenario correlation.  A non-PSD result is rejected by
    ``stress_pair_correlation``; it is never repaired or substituted.
    """
    if not np.isfinite(adjustment):
        raise ValidationError("Correlation adjustment must be finite.")
    historical = pair_correlation(estimates, ticker_a, ticker_b)
    scenario = historical + adjustment
    if not -1 <= scenario <= 1:
        raise ValidationError(
            f"Correlation scenario is invalid: historical {historical:.4f} plus adjustment {adjustment:.4f} is outside [-1, 1]."
        )
    return stress_pair_correlation(estimates, ticker_a, ticker_b, scenario), historical, scenario


def portfolio_metrics(weights: pd.Series | dict[str, float], estimates: Estimates) -> dict[str, float]:
    w = validate_weights(weights).to_numpy()
    mean = estimates.mean.reindex(TICKERS).to_numpy()
    covariance = validate_covariance(estimates.covariance.loc[TICKERS, TICKERS])
    variance = float(w @ covariance @ w)
    return {"return": float(w @ mean), "volatility": float(np.sqrt(max(variance, 0.0))), "reserve": float(sum(w[i] for i, t in enumerate(TICKERS) if t in RESERVE_ELIGIBLE))}


def equal_weight() -> pd.Series:
    return pd.Series(0.25, index=TICKERS)


def inverse_volatility(estimates: Estimates) -> pd.Series:
    vol = np.sqrt(np.diag(validate_covariance(estimates.covariance.loc[TICKERS, TICKERS])))
    if np.any(vol <= 0):
        raise ValidationError("Inverse-volatility weights require positive asset volatilities.")
    return pd.Series((1 / vol) / (1 / vol).sum(), index=TICKERS)


def grid_minimum_volatility(estimates: Estimates, return_target: float, reserve_minimum: float, step: float = 0.05, starting: pd.Series | dict[str, float] | None = None, turnover_limit: float | None = None) -> pd.Series:
    """Transparent five-percentage-point search retained from Lab 15."""
    if not 0 <= reserve_minimum <= 1 or not 0 <= return_target <= 1 or step <= 0:
        raise ValidationError("Target and reserve must be decimal rates between 0 and 1; step must be positive.")
    if turnover_limit is not None:
        if starting is None:
            raise ValidationError("A starting portfolio is required when turnover is constrained.")
        validate_weights(starting)
        if not 0 <= turnover_limit <= 1:
            raise ValidationError("Turnover limit must be a decimal rate between 0 and 1.")
    units = round(1 / step)
    if not np.isclose(units * step, 1.0):
        raise ValidationError("Grid step must evenly divide 100%.")
    best: tuple[float, pd.Series] | None = None
    for a, b, c in product(range(units + 1), repeat=3):
        d = units - a - b - c
        if d < 0: continue
        w = pd.Series(np.array([a, b, c, d]) * step, index=TICKERS)
        metrics = portfolio_metrics(w, estimates)
        if metrics["reserve"] + 1e-12 < reserve_minimum or metrics["return"] + 1e-12 < return_target:
            continue
        if turnover_limit is not None and turnover_and_cost(w, starting, 0)["turnover"] > turnover_limit + 1e-12:
            continue
        if best is None or metrics["volatility"] < best[0] - 1e-12:
            best = (metrics["volatility"], w)
    if best is None:
        constraint = " and turnover limit" if turnover_limit is not None else ""
        raise ValidationError("INFEASIBLE: no five-percentage-point portfolio meets the reserve, modeled return threshold" + constraint + ".")
    return best[1]


def turnover_and_cost(target: pd.Series | dict[str, float], starting: pd.Series | dict[str, float], cost_bps: float) -> dict[str, float]:
    target_w, starting_w = validate_weights(target), validate_weights(starting)
    if not np.isfinite(cost_bps) or cost_bps < 0:
        raise ValidationError("Transaction cost must be a non-negative number of basis points.")
    turnover = 0.5 * float((target_w - starting_w).abs().sum())  # one-way turnover convention
    return {"turnover": turnover, "cost": turnover * cost_bps / 10_000}


def net_return_metrics(gross_annual_return: float, one_time_cost: float, horizon_years: int = 5) -> dict[str, float]:
    """Show implementation costs once, plus an illustrative annualized horizon drag.

    Cost is paid at implementation, not subtracted every year.  The five-year
    proxy spreads its compounded effect over the IPS evaluation horizon solely
    for comparability with an annual return threshold.
    """
    if not np.isfinite(gross_annual_return) or not np.isfinite(one_time_cost) or one_time_cost < 0:
        raise ValidationError("Gross return and one-time cost must be finite; cost cannot be negative.")
    if horizon_years <= 0:
        raise ValidationError("Cost horizon must be positive.")
    annualized_drag = 1 - (1 - one_time_cost) ** (1 / horizon_years)
    return {
        "gross_annual_return": gross_annual_return,
        "one_time_implementation_cost": one_time_cost,
        "first_year_return_after_cost": gross_annual_return - one_time_cost,
        "five_year_annualized_cost_drag": annualized_drag,
        "five_year_net_return_proxy": gross_annual_return - annualized_drag,
    }


def mandate_verdicts(weights: pd.Series, metrics: dict[str, float], modeled_target: float, turnover: float, turnover_limit: float) -> pd.DataFrame:
    checks = [
        ("Weights sum to 100%", "PASS", "Arithmetic check."),
        ("Long-only / no borrowing / direct derivatives", "PASS", "All model weights are non-negative; ETF look-through is not assessed."),
        ("3% BIL reserve", "PASS" if metrics["reserve"] >= 0.03 - 1e-12 else "FAIL", "BIL only is reserve-eligible; IEF is not treated as cash."),
        ("Modeled five-year net return proxy", "PASS" if metrics["five_year_net_return_proxy"] >= modeled_target - 1e-12 else "FAIL", "Historical gross mean less annualized one-time implementation-cost drag; not proof of CPI + 4% achievement."),
        ("Annual one-way turnover limit", "PASS" if turnover <= turnover_limit + 1e-12 else "FAIL", "From the stated starting weights; approval may be required if exceeded."),
        ("8% nonexempt issuer exposure", "NOT VERIFIED", "ETF-level ticker data do not establish issuer look-through or exemption evidence."),
        ("90% redeemable within five business days", "NOT VERIFIED", "No execution, settlement, or ETF liquidity evidence is bundled."),
        ("Seven-year horizon", "NOT VERIFIED", "Investor horizon cannot be tested from market data."),
        ("Rolling five-year CPI + 4%, net of costs", "NOT VERIFIED", "CPI series, cost history, and five-year realized periods are not in this model."),
        ("Calendar-year loss rule", "NOT VERIFIED", "CIO has not defined the loss measure or breach response."),
    ]
    return pd.DataFrame(checks, columns=["Rule", "Verdict", "Reason"])


def _portfolio_record(weights: pd.Series, estimates: Estimates, return_target: float, starting: pd.Series, turnover_limit: float, cost_bps: float, status: str) -> dict:
    metrics = portfolio_metrics(weights, estimates)
    trade = turnover_and_cost(weights, starting, cost_bps)
    metrics.update(net_return_metrics(metrics["return"], trade["cost"]))
    benchmark_metrics = portfolio_metrics(BENCHMARK, estimates)
    return {"status": status, "weights": weights, "metrics": metrics, "benchmark_relative": {"return": metrics["return"] - benchmark_metrics["return"], "volatility": metrics["volatility"] - benchmark_metrics["volatility"]}, "trade": trade, "verdicts": mandate_verdicts(weights, metrics, return_target, trade["turnover"], turnover_limit)}


def compare_portfolios(estimates: Estimates, return_target: float, reserve_minimum: float, starting: pd.Series, turnover_limit: float, cost_bps: float) -> dict[str, dict]:
    """Compare methods while keeping an approval-required unconstrained result."""
    starting = validate_weights(starting)
    portfolios = {
        "Equal weight": (equal_weight(), "COMPARISON ONLY"),
        "Inverse volatility": (inverse_volatility(estimates), "COMPARISON ONLY"),
    }
    result: dict[str, dict] = {}
    for name, (weights, status) in portfolios.items():
        result[name] = _portfolio_record(weights, estimates, return_target, starting, turnover_limit, cost_bps, status)
    try:
        unconstrained = grid_minimum_volatility(estimates, return_target, reserve_minimum)
        result["Unconstrained minimum volatility (committee approval required)"] = _portfolio_record(unconstrained, estimates, return_target, starting, turnover_limit, cost_bps, "EXCEEDS TURNOVER WITHOUT APPROVAL")
    except ValidationError as exc:
        result["Unconstrained minimum volatility (committee approval required)"] = {"status": "INFEASIBLE", "reason": str(exc)}
    try:
        constrained = grid_minimum_volatility(estimates, return_target, reserve_minimum, starting=starting, turnover_limit=turnover_limit)
        result["Turnover-constrained minimum volatility"] = _portfolio_record(constrained, estimates, return_target, starting, turnover_limit, cost_bps, "FEASIBLE")
    except ValidationError as exc:
        result["Turnover-constrained minimum volatility"] = {"status": "INFEASIBLE", "reason": str(exc)}
    return result
