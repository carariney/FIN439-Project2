# Meridian Foundation Portfolio Decision Lab

AI tools used: OpenAI Codex assisted with code structure, tests, and documentation; it did not generate, download, or validate market observations.

The analysis and decision are mine, for education rather than investment advice.

This Streamlit application compares equal-weight, inverse-volatility, an approval-required unconstrained minimum-volatility comparison, and a transparent five-percentage-point turnover-constrained minimum-volatility allocation of BIL, IEF, AGG, and ACWI. It fails closed: it uses `prices.csv` at repository root and will not download substitute data.

`mandate.py` is retained as historical Lab 13 teaching material and is not the Project 2 portfolio engine. Project 2 ETF calculations, including the BIL-only reserve-eligibility rule, are governed by `portfolio.py`.

## Current evidence status

The bundled [`prices.csv`](prices.csv) and [`Project-2-Data-Sources.md`](Project-2-Data-Sources.md) define the frozen input: 60 monthly period labels from October 2021–September 2026 and `Date,BIL,IEF,AGG,ACWI`. A 54-row March-2026 file stops and reports April–September as missing. Labels are periods, not confirmed publication/trade timestamps.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 run_model.py
python3 -m streamlit run app.py
```

`run_model.py` writes `output/project2-visible-output.json`; it exits nonzero while the data is unavailable. Rates are decimals in code and percentages in the interface. Returns are annualized historical means or explicit forecast overrides, never promises. Turnover is one-way: `0.5 × sum(abs(target − starting))`; cost is turnover × basis points / 10,000. Costs are one-time implementation costs; the displayed five-year annualized cost drag is an illustrative comparison proxy, not a recurring annual charge. The 25% turnover limit is a hard optimizer constraint; an infeasible case is reported as `INFEASIBLE`, never silently relaxed.

### Reproducible command options

`--reserve-minimum` accepts a decimal rate from 0 to 1 and defaults to `0.03`. `--output` writes a JSON record to a separate path, so a scenario need not overwrite the frozen baseline.

```bash
python3 run_model.py --reserve-minimum 0.04 --output output/example-scenario.json
```

The completed locked protocol used the same syntax with a 30% reserve minimum and saved separate evidence without overwriting the baseline. See the [locked record](docs/locked-changed-input-record.md) and [manifest](docs/submission-manifest.md). Do not execute additional changed-input cases without a new independently authored and committed prediction.

The ACWI–AGG correlation control is an **adjustment**, not an absolute replacement. A zero adjustment uses each estimation window's own historical correlation; the same adjustment is then applied and validated separately to the 59- and 36-return windows. A non-positive-semidefinite scenario is displayed as unavailable and is never repaired.

BIL only is reserve eligible; IEF is not automatically cash-equivalent. Liquidity, issuer look-through, and other unavailable evidence remain `NOT VERIFIED`. See [data card](docs/project2-data-card.md), [memo](docs/decision-memo.md), [validation record](docs/validation-and-ai-use.md), and [manifest](docs/submission-manifest.md).
