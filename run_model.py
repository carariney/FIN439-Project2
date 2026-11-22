"""Create visible, reproducible model output without downloading market data."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from portfolio import ValidationError, load_prices, estimate, compare_portfolios, BENCHMARK

ROOT = Path(__file__).parent
OUT = ROOT / "output" / "project2-visible-output.json"

def decimal_rate(value: str) -> float:
    try:
        rate = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a decimal rate, for example 0.03") from exc
    if not 0 <= rate <= 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1 as a decimal rate")
    return rate


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen Meridian Foundation baseline or a separately saved scenario.")
    parser.add_argument("--reserve-minimum", type=decimal_rate, default=0.03, help="BIL reserve minimum as a decimal rate (default: 0.03).")
    parser.add_argument("--output", type=Path, default=OUT, help=f"JSON output path (default: {OUT.relative_to(ROOT)}).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    inputs = {"data_cutoff": "2026-09 period label", "window_monthly_returns": 59, "inflation_assumption": 0.025, "proxy_return_target": 0.065, "reserve_minimum": args.reserve_minimum, "turnover_limit": 0.25, "transaction_cost_bps": 10, "transaction_cost_treatment": "One-time implementation cost; five-year annualized drag shown only as an illustrative proxy.", "starting_weights": BENCHMARK.to_dict()}
    try:
        prices = load_prices(ROOT / "prices.csv")
        estimates = estimate(prices)
        result = compare_portfolios(estimates, inputs["proxy_return_target"], inputs["reserve_minimum"], BENCHMARK, inputs["turnover_limit"], inputs["transaction_cost_bps"])
        serial = {}
        for name, item in result.items():
            if item["status"] == "INFEASIBLE":
                serial[name] = item
            else:
                serial[name] = {"status": item["status"], "weights": item["weights"].to_dict(), "metrics": item["metrics"], "benchmark_relative": item["benchmark_relative"], "trade": item["trade"], "verdicts": item["verdicts"].to_dict(orient="records")}
        constrained = result["Turnover-constrained minimum volatility"]
        if constrained["status"] == "INFEASIBLE":
            basis = "STOP: turnover-constrained strategy is infeasible; do not relax the return objective or turnover limit without committee action."
            window_sensitivity = {"status": "NOT ASSESSED", "reason": "Base turnover-constrained strategy is infeasible."}
        else:
            failures = constrained["verdicts"].query("Verdict == 'FAIL'")
            alternate = compare_portfolios(estimate(prices, window=36), inputs["proxy_return_target"], inputs["reserve_minimum"], BENCHMARK, inputs["turnover_limit"], inputs["transaction_cost_bps"])["Turnover-constrained minimum volatility"]
            if alternate["status"] == "INFEASIBLE":
                window_sensitivity = {"status": "INFEASIBLE", "reason": "36-return turnover-constrained scenario is infeasible."}
                basis = "STOP: turnover-constrained strategy is infeasible under the 36-return estimation window."
            else:
                max_change = float((constrained["weights"] - alternate["weights"]).abs().max())
                window_sensitivity = {"status": "ASSESSED", "comparison_window_monthly_returns": 36, "base_weights": constrained["weights"].to_dict(), "comparison_weights": alternate["weights"].to_dict(), "largest_allocation_change": max_change, "material_threshold": 0.20}
                if len(failures):
                    basis = "SUSPEND: a hard modeled mandate rule fails."
                elif max_change >= .20 - 1e-12:
                    basis = "STOP: allocation changes by at least 20 percentage points between 59- and 36-return windows; estimation instability requires committee resolution."
                else:
                    basis = "Committee review required: modeled constraints pass, but material policy rules remain NOT VERIFIED."
        record = {"status": "completed", "inputs": inputs, "portfolios": serial, "window_sensitivity": window_sensitivity, "recommendation_basis": basis, "stopping_conditions": ["Turnover-constrained strategy is INFEASIBLE.", "Any hard modeled mandate rule is FAIL.", "Largest allocation change across 36- versus 59-return windows is at least 20 percentage points."], "unconstrained_comparison_note": "The unconstrained minimum-volatility result is retained only to show the effect of waiving turnover; it is not a compliant recommendation."}
    except ValidationError as exc:
        record = {"status": "blocked", "inputs": inputs, "recommendation_basis": "No portfolio recommendation: validated bundled prices.csv is unavailable or invalid.", "blocker": str(exc)}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(output_path)
    print(record["status"])
    return 0 if record["status"] == "completed" else 2
if __name__ == "__main__": raise SystemExit(main())
