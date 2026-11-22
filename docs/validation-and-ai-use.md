# Validation and AI-use record

## Completed evidence

- Repository audit: branch `main`, remote `origin` observed; unrelated Project 1 materials were not edited.
- Code contains strict price, weight, covariance, infeasibility, turnover, transaction-cost, correlation-stress, and provenance checks.
- Test suite covers Lab 13 candidate/negative-weight mechanics, Lab 14 arithmetic, Lab 16 known answers, actual-data duplicate dates, invalid prices/covariance, infeasibility, turnover/costs, turnover-constrained optimization, correlation sensitivity, and 36-versus-59-return windows.
- The initial repository audit found no root `prices.csv`, `portfolio.py`, root `app.py`, or `Project-2-Data-Sources.md`. The original price file and source record were subsequently restored and validated; the engine does not fabricate their data contents.
- The correlation-stress regression uses each window's own historical ACWI–AGG correlation plus the same adjustment; an invalid covariance scenario is surfaced rather than repaired.
- `run_model.py` validates `--reserve-minimum` as a decimal rate and can write a scenario to a separate `--output` path without replacing baseline output.

## Reserve-reporting defect and correction

The committed 30% BIL reserve evidence exposed a reporting defect: the optimizer received the scenario reserve input correctly, but `mandate_verdicts` used a hardcoded `0.03` threshold and the fixed label `3% BIL reserve`. As a result, comparison-portfolio reserve verdicts could be wrong when the scenario reserve differed from 3%; for example, a 25% BIL portfolio was displayed as passing in the 30% scenario.

The correction passes `reserve_minimum` through the portfolio-record and mandate-verdict paths, validates it as a decimal rate, and renders the actual scenario label. Regression tests now confirm that 25% BIL passes a 3% reserve requirement and fails a 30% requirement. The default 3% calculation is also compared in memory with the frozen baseline JSON, without overwriting that evidence.

The original locked output and post-run record remain preserved evidence of the defect. Remaining limitation: comparison-portfolio mandate verdicts from the original 30% scenario should be read as historical evidence of the defect, not corrected results; the turnover-constrained optimizer's `INFEASIBLE` result itself was based on the actual 30% input.

## Pending manual evidence

- A checksum or other independent preservation record for the original `prices.csv`.
- CIO clarification of calendar-year loss and optimization priority.
- Liquidity/redemption, issuer-exemption/look-through, derivative exposure, and transaction-cost evidence.
- Publication-time evidence for the monthly Yahoo adjusted-price observations; period labels alone do not establish point-in-time availability.
- An approved correlation scenario; the implemented 20-percentage-point 36-versus-59-return-window stop threshold is a model guardrail requiring committee confirmation.
- Video links, durations, transcripts, access checks, submission receipt, and any Git commit IDs supplied by the student.
- The locked changed-input prediction and pre-run commit below.

## AI disclosure

OpenAI Codex was used for implementation assistance on this date. It was used to structure the fail-closed Python/Streamlit application, tests, and draft documentation. It must not be represented as a source of price data, manual evidence, an AI-off prediction, a precommit, test execution, video, transcript, or submission receipt.

## Locked Changed-Input Record — DO NOT EXECUTE YET

The proposed meaningful perturbation is: change the **final engine's BIL reserve minimum** from 3.0% to 10.0%, holding the original validated price file, return target, window, starting weights, transaction costs, and grid step constant. This can change constrained weights, feasibility, estimated volatility, turnover, costs, and the decision guardrail.

After the human prediction commit exists, the preplanned command is `python3 run_model.py --reserve-minimum 0.10 --output output/locked-reserve-minimum-010.json`. It has not been executed. The distinct output path preserves `output/project2-visible-output.json` as the baseline record.

The human must first edit `docs/locked-changed-input-record.md` with an AI-off prediction in their own words, including the old/new input and units, expected direction and reason, expected committee effect, and reversal condition. Then commit that file alone (or with no model-output files) to GitHub before executing the test. Do not amend or backdate it.

After the commit exists, record its hash in the template, run the supplied command, append observed output and reconciliation, and commit the second record. This document intentionally does not provide the human prediction.
