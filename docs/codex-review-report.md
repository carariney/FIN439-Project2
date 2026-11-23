# Project 2 Codex Review Report

Date: 2026-11-23

Scope

This review was performed only in `/Users/carariney/Desktop/FIN439-Project2`. No commit or push was performed.

Changes completed

- `app.py`: the mandate-test summary now explicitly constructs its display DataFrame with pandas `string` dtype. This keeps all portfolio names, counts, and infeasibility placeholders as consistent display values, preventing Arrow type reconciliation warnings. The existing visual design and STOP logic were left intact.
- `docs/project2-data-card.md`: added a short, clearly labelled teaching example of a provenance-valid but economically implausible ETF observation. It explicitly states that it does not change `prices.csv`, signals, or results.
- `docs/validation-and-ai-use.md`: recorded the exact SHA-256 for `prices.csv` and the verification command.
- `README.md`: states that `mandate.py` is retained Lab 13 teaching material and that `portfolio.py` governs the actual Project 2 reserve rule.
- `docs/locked-changed-input-record.md`: added a clarification above the frozen Prediction section. The frozen Prediction section, including its blank pre-run-hash field, was left byte-for-byte unchanged.

Price-file integrity

SHA-256 of `prices.csv`:

`df1ca3ff8e9f4f12680adbb1dce73fd8e9cd61775bddde4cd93b26e57b6aa876`

Verification command, from the repository root:

`shasum -a 256 prices.csv`

Validation performed

- Ran `python3 -m pytest -q`: 15 passed in 19.39 seconds.
- Pytest emitted two non-test failures: `PytestCacheWarning` messages because the sandbox could not create `.pytest_cache` files. They did not affect the 15 passing tests.
- The default-model regression test passed. It compares current default calculations in memory against `output/project2-visible-output.json`; the protected baseline output was not rewritten.
- `git diff --exit-code -- output/project2-visible-output.json output/locked-reserve-minimum-030.json` produced no differences. Neither protected output changed.
- Inspected, but did not rerun, the locked 30% reserve scenario. Its existing evidence records `reserve_minimum: 0.3`, an `INFEASIBLE` turnover-constrained result, and the STOP instruction not to relax the return target or turnover limit.
- Confirmed the 3% and 30% reserve verdict regression test passed: 25% BIL passes at 3% and fails at 30%.
- Compared the entire frozen Prediction block with pre-run commit `d463d00ec290be407ac79d26475f29dbfe21b0a7`; it is byte-for-byte identical.
- Ran `git diff --check`: no whitespace errors.

Files changed for this request

- `app.py`
- `README.md`
- `docs/project2-data-card.md`
- `docs/validation-and-ai-use.md`
- `docs/locked-changed-input-record.md`
- `docs/codex-review-report.md` (this report)

Protected items

The optimizer, financial calculations, `prices.csv`, `output/project2-visible-output.json`, `output/locked-reserve-minimum-030.json`, the frozen Prediction section, and `.streamlit/config.toml` were not modified. The locked 30% scenario command was not rerun.

Working-tree note

At the start of this work, the first five files above already had uncommitted changes. This review retained those requested changes and added the explicit `string` display dtype in `app.py` plus this report. An untracked `.streamlit/` directory was also present and was not touched.
