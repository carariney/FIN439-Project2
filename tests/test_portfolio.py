import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from portfolio import (ValidationError, Estimates, TICKERS, BENCHMARK, validate_weights, validate_covariance, monthly_returns, estimate, portfolio_metrics, grid_minimum_volatility, turnover_and_cost, net_return_metrics, mandate_verdicts, load_prices, compare_portfolios, pair_correlation, stress_pair_correlation, apply_correlation_adjustment)
from asof import lab16_known_answers
from run_model import parse_args

def sample_prices(n=60):
    # ISO labels are sufficient for return arithmetic and avoid asserting a
    # native datetime dependency in the test fixture.
    dates = [f"{2021 + (9 + i) // 12:04d}-{(9 + i) % 12 + 1:02d}-01" for i in range(n)]
    return pd.DataFrame({t: 100 * (1 + .002 * (i + 1)) ** np.arange(n) for i,t in enumerate(TICKERS)}, index=dates)

def test_lab13_known_answers_and_negative_weight_probe():
    metrics = {"reserve": .03, "return": .07, **net_return_metrics(.07, 0)}
    assert mandate_verdicts(pd.Series([.03,0,0,.97], index=TICKERS), metrics, .065, .1, .25).query("Rule == '3% BIL reserve'").iloc[0].Verdict == "PASS"
    with pytest.raises(ValidationError): validate_weights({"BIL": -.02,"IEF":0,"AGG":.38,"ACWI":.64})

def test_lab14_arithmetic_and_independent_metric():
    e = Estimates(pd.Series([.12,.06,.05,.10], index=TICKERS), pd.DataFrame(np.diag([.04,.01,.01,.09]), index=TICKERS, columns=TICKERS), pd.DataFrame())
    m = portfolio_metrics({"BIL":.25,"IEF":.25,"AGG":.25,"ACWI":.25}, e)
    assert m["return"] == pytest.approx(.0825)
    assert m["volatility"] == pytest.approx(np.sqrt(.15/16))

def test_lab16_provenance_known_answers():
    asof, naive, retained = lab16_known_answers()
    assert retained.row_id.tolist() == [1,4,5,6,9,12]
    assert asof.to_dict() == pytest.approx({"AAA":.0198,"BBB":-.0102,"CCC":.0091})
    assert naive.to_dict() == pytest.approx({"AAA":.0583,"BBB":-.0515,"CCC":.0182})

def test_returns_and_estimation_window_sensitivity():
    p = sample_prices(); assert len(monthly_returns(p)) == 59
    assert len(estimate(p,36).returns) == 36 and len(estimate(p,59).returns) == 59

def test_covariance_validation_and_infeasibility():
    with pytest.raises(ValidationError): validate_covariance(np.ones((4,4)) * np.nan)
    bad = np.eye(4); bad[0,1] = .5
    with pytest.raises(ValidationError): validate_covariance(bad)
    not_psd = np.eye(4); not_psd[0,1] = not_psd[1,0] = 2
    with pytest.raises(ValidationError): validate_covariance(not_psd)
    e = estimate(sample_prices())
    with pytest.raises(ValidationError): grid_minimum_volatility(e, .99, .03)

def test_turnover_and_cost():
    result = turnover_and_cost({"BIL":.5,"IEF":0,"AGG":.5,"ACWI":0}, BENCHMARK, 10)
    assert result["turnover"] == pytest.approx(.6)
    assert result["cost"] == pytest.approx(.0006)
    net = net_return_metrics(.08, result["cost"])
    assert net["first_year_return_after_cost"] == pytest.approx(.0794)
    assert 0 < net["five_year_annualized_cost_drag"] < result["cost"]

def test_loader_missing_file_and_invalid_prices(tmp_path):
    with pytest.raises(ValidationError): load_prices(tmp_path / "none.csv")
    bad = sample_prices(); bad.insert(0,"Date",bad.index); bad.loc[0,"BIL"] = -1
    path = tmp_path / "prices.csv"; bad.to_csv(path,index=False)
    with pytest.raises(ValidationError): load_prices(path)


def test_actual_data_duplicate_month_is_rejected(tmp_path):
    actual = pd.read_csv(Path(__file__).parents[1] / "prices.csv")
    assert len(actual) == 60
    actual.loc[1, "Date"] = actual.loc[0, "Date"]
    path = tmp_path / "duplicate-prices.csv"
    actual.to_csv(path, index=False)
    with pytest.raises(ValidationError, match="unique and chronological"):
        load_prices(path)


def test_turnover_constrained_optimizer_and_infeasibility():
    actual = load_prices(Path(__file__).parents[1] / "prices.csv")
    e = estimate(actual)
    result = compare_portfolios(e, .065, .03, BENCHMARK, .25, 10)
    constrained = result["Turnover-constrained minimum volatility"]
    assert constrained["status"] == "FEASIBLE"
    assert constrained["trade"]["turnover"] <= .25 + 1e-12
    assert result["Unconstrained minimum volatility (committee approval required)"]["trade"]["turnover"] > .25
    infeasible = compare_portfolios(e, .30, .03, BENCHMARK, .25, 10)
    assert infeasible["Turnover-constrained minimum volatility"]["status"] == "INFEASIBLE"


def test_correlation_scenario_changes_covariance_and_volatility():
    actual = load_prices(Path(__file__).parents[1] / "prices.csv")
    base = estimate(actual)
    historical = pair_correlation(base, "ACWI", "AGG")
    stressed_assumption = historical - .05
    stressed = stress_pair_correlation(base, "ACWI", "AGG", stressed_assumption)
    assert pair_correlation(stressed, "ACWI", "AGG") == pytest.approx(stressed_assumption)
    assert portfolio_metrics(BENCHMARK, base)["volatility"] != pytest.approx(portfolio_metrics(BENCHMARK, stressed)["volatility"])


def test_actual_data_estimation_window_sensitivity_is_reportable():
    actual = load_prices(Path(__file__).parents[1] / "prices.csv")
    result_59 = compare_portfolios(estimate(actual, 59), .065, .03, BENCHMARK, .25, 10)
    result_36 = compare_portfolios(estimate(actual, 36), .065, .03, BENCHMARK, .25, 10)
    for result in (result_59, result_36):
        constrained = result["Turnover-constrained minimum volatility"]
        assert constrained["status"] in {"FEASIBLE", "INFEASIBLE"}
        if constrained["status"] == "FEASIBLE":
            assert constrained["trade"]["turnover"] <= .25 + 1e-12


def test_window_specific_correlation_baselines_are_stable_at_default_and_valid_stress():
    actual = load_prices(Path(__file__).parents[1] / "prices.csv")
    estimates_59, estimates_36 = estimate(actual, 59), estimate(actual, 36)
    historical_59 = pair_correlation(estimates_59, "ACWI", "AGG")
    historical_36 = pair_correlation(estimates_36, "ACWI", "AGG")
    assert historical_59 != pytest.approx(historical_36)
    for adjustment in (0.0, -0.05):
        stressed_59, base_59, scenario_59 = apply_correlation_adjustment(estimates_59, "ACWI", "AGG", adjustment)
        stressed_36, base_36, scenario_36 = apply_correlation_adjustment(estimates_36, "ACWI", "AGG", adjustment)
        assert base_59 == pytest.approx(historical_59)
        assert base_36 == pytest.approx(historical_36)
        assert scenario_59 == pytest.approx(historical_59 + adjustment)
        assert scenario_36 == pytest.approx(historical_36 + adjustment)
        assert compare_portfolios(stressed_59, .065, .03, BENCHMARK, .25, 10)["Turnover-constrained minimum volatility"]["status"] == "FEASIBLE"
        assert compare_portfolios(stressed_36, .065, .03, BENCHMARK, .25, 10)["Turnover-constrained minimum volatility"]["status"] == "FEASIBLE"


def test_cli_default_and_argument_validation_without_running_locked_scenario():
    defaults = parse_args([])
    assert defaults.reserve_minimum == pytest.approx(.03)
    custom = parse_args(["--reserve-minimum", "0.04", "--output", "output/safe-parser-test.json"])
    assert custom.reserve_minimum == pytest.approx(.04)
    assert custom.output == Path("output/safe-parser-test.json")
    with pytest.raises(SystemExit):
        parse_args(["--reserve-minimum", "1.01"])
