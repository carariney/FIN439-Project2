# Validation and AI-use record

## Completed evidence

- Repository audit: branch `main`, remote `origin` observed; unrelated Project 1 materials were not edited.
- Code contains strict price, weight, covariance, infeasibility, turnover, transaction-cost, correlation-stress, and provenance checks.
- Test suite covers Lab 13 candidate/negative-weight mechanics, Lab 14 arithmetic, Lab 16 known answers, actual-data duplicate dates, invalid prices/covariance, infeasibility, turnover/costs, turnover-constrained optimization, correlation sensitivity, scenario-aware reserve reporting, and 36-versus-59-return windows.
- The initial repository audit found no root `prices.csv`, `portfolio.py`, root `app.py`, or `Project-2-Data-Sources.md`. The original price file and source record were subsequently restored and validated; the engine does not fabricate their data contents.
- The correlation-stress regression uses each window's own historical ACWI–AGG correlation plus the same adjustment; an invalid covariance scenario is surfaced rather than repaired.
- `run_model.py` validates `--reserve-minimum` as a decimal rate and can write a scenario to a separate `--output` path without replacing baseline output.
- Latest executed test result: **15 passed**. This is reported from the most recent validated test run; no separate test log was created or claimed.

## Git evidence

| Evidence | Commit |
| --- | --- |
| Frozen baseline | [`1bbd4454d73891a22acfe959934c23d17a993d50`](https://github.com/carariney/FIN439-Project2/commit/1bbd4454d73891a22acfe959934c23d17a993d50) |
| Final pre-run freeze | [`d463d00ec290be407ac79d26475f29dbfe21b0a7`](https://github.com/carariney/FIN439-Project2/commit/d463d00ec290be407ac79d26475f29dbfe21b0a7) |
| Locked-test post-run evidence | [`bab663c095b1937fa1cf61201ad49fad41e0e2f9`](https://github.com/carariney/FIN439-Project2/commit/bab663c095b1937fa1cf61201ad49fad41e0e2f9) |
| Reserve-reporting correction | [`a0277cb238edb8adeb880b1f70166cea5922c152`](https://github.com/carariney/FIN439-Project2/commit/a0277cb238edb8adeb880b1f70166cea5922c152) |

## Reserve-reporting defect and correction

The committed 30% BIL reserve evidence exposed a reporting defect: the optimizer received the scenario reserve input correctly, but `mandate_verdicts` used a hardcoded `0.03` threshold and the fixed label `3% BIL reserve`. As a result, comparison-portfolio reserve verdicts could be wrong when the scenario reserve differed from 3%; for example, a 25% BIL portfolio was displayed as passing in the 30% scenario.

The correction passes `reserve_minimum` through the portfolio-record and mandate-verdict paths, validates it as a decimal rate, and renders the actual scenario label. Regression tests now confirm that 25% BIL passes a 3% reserve requirement and fails a 30% requirement. The default 3% calculation is also compared in memory with the frozen baseline JSON, without overwriting that evidence.

The original locked output and post-run record remain preserved evidence of the defect. The separate correction at `a0277cb238edb8adeb880b1f70166cea5922c152` changed reporting and regression tests only; it did not rewrite frozen output. Remaining limitation: comparison-portfolio mandate verdicts from the original 30% scenario should be read as historical evidence of the defect, not corrected results; the turnover-constrained optimizer's `INFEASIBLE` result itself was based on the actual 30% input.

## Completed Locked Changed-Input Record

The completed changed input raised the BIL reserve minimum from **3% to 30%**, holding the bundled price data, 59-return estimation window, 6.5% proxy target, 60% ACWI / 40% AGG starting weights, 25% one-way turnover limit, 10-basis-point one-time cost, and 5-percentage-point grid constant.

Executed command:

```bash
python3 run_model.py --reserve-minimum 0.30 --output output/locked-reserve-minimum-030.json
```

The turnover-constrained optimizer was **INFEASIBLE**: no grid portfolio simultaneously met the 30% reserve, modeled return threshold, and turnover limit. The prediction was partially supported: its implied feasible higher-BIL allocation was not observed, its uncertainty about constraint satisfaction resolved negatively, and its expected STOP committee action held. The committee decision remains **STOP**; the process must not relax the return target or turnover limit without committee action. See the preserved [post-run record](locked-changed-input-record.md) and [separate scenario output](../output/locked-reserve-minimum-030.json).

## Pending manual evidence

- A checksum or other independent preservation record for the original `prices.csv`.
- CIO clarification of calendar-year loss and optimization priority.
- Liquidity/redemption, issuer-exemption/look-through, derivative exposure, and transaction-cost evidence.
- Publication-time evidence for the monthly Yahoo adjusted-price observations; period labels alone do not establish point-in-time availability.
- An approved correlation scenario; the implemented 20-percentage-point 36-versus-59-return-window stop threshold is a model guardrail requiring committee confirmation.
- Video links, durations, transcripts, access checks, submission receipt, and any Git commit IDs supplied by the student.

## AI disclosure

OpenAI Codex was used for implementation assistance on the Python/Streamlit application, tests, and documentation. It did not generate or download market observations. The repository records a student-entered locked prediction and its Git history, but the repository alone cannot independently prove the circumstances of authorship. In this workflow, Codex did not draft or edit the Prediction section after the AI-off boundary; this disclosure does not make a broader AI-off authorship claim without independent evidence.
