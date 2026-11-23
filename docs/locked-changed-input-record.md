# Locked Changed-Input Record — Human AI-off section required

> **Record status: COMPLETE.** The Prediction section below is preserved byte-for-byte as frozen at the pre-run commit. The original prediction commit is `49716cf`; final pre-run freeze is `d463d00ec290be407ac79d26475f29dbfe21b0a7`; post-run evidence is `bab663c095b1937fa1cf61201ad49fad41e0e2f9`. The blank hash field inside Prediction is retained because it is part of that frozen section.

## Prediction (complete yourself, with AI off)

Date/time: 11/22/2026
Final-engine file and command to be run: run_model.py — python3 run_model.py --reserve-minimum 0.30 --output output/locked-reserve-minimum-030.json
Input changed (old value, new value, units): Minimum BIL reserve allocation increases from 3% to 30% of the portfolio. All other inputs remain unchanged.
Expected direction of weights/return/volatility/turnover/decision: I expect the portfolio to increase its BIL allocation from 25% to at least 30%. This will leave less room for the other investments, so I expect the optimizer to reduce one or more of those positions. BIL is a lower-risk investment, and I expect volatility to decrease, although the estimated return may also decline. Turnover could increase because the portfolio has to adjust to the higher reserve requirement. I am less certain whether the model will still meet its return and turnover constraints.
Why (model constraint or assumption): The optimizer must satisfy the minimum reserve requirement while also meeting its return objective and other portfolio restrictions. Raising the BIL minimum above the current allocation makes the constraint more restrictive and could force the model to sacrifice return or change its allocation.
Expected committee action and reversal condition: I expect the committee's current STOP recommendation to remain in place because the original portfolio already showed sensitivity to the estimation window. I would reconsider that decision if the revised portfolio satisfies the mandate, remains stable under the required stress tests, and resolves the outstanding compliance checks.

Pre-run commit hash: To be added to the validation record after committing this prediction.

## Execute only after the pre-run commit

- Command: `python3 run_model.py --reserve-minimum 0.30 --output output/locked-reserve-minimum-030.json`
- Output file/location: `output/locked-reserve-minimum-030.json`
- Observed change (with units): Reserve minimum changed from 3% to 30%. The turnover-constrained minimum-volatility optimizer is INFEASIBLE: no 5-percentage-point allocation meets the 30% reserve, modeled return threshold, and 25% one-way turnover limit simultaneously. Therefore no constrained portfolio weights, return, volatility, or turnover are available for comparison. The approval-required unconstrained comparison remains 60% BIL / 40% ACWI with 60% one-way turnover.
- Comparison to prediction: The expected higher BIL allocation was not observed because the constrained solution became infeasible. The uncertainty about whether return and turnover constraints would remain satisfied was resolved negatively. The expected STOP recommendation remains in place.
- First broken assumption/unit/sign/date/interface if prediction differed: The prediction implicitly assumed a feasible constrained allocation would exist. The first binding issue is constraint infeasibility, not a unit, sign, date, or interface error.
- Reporting defect discovered: comparison-portfolio mandate output still hardcodes the label and threshold `3% BIL reserve`; at this 30% scenario it incorrectly reports the 25% BIL equal-weight comparison as passing. The constrained optimizer itself applied the 30% input and reported INFEASIBLE. This defect is documented here and is not fixed in this evidence commit.
- Final action: `ACTION HOLDS` — STOP; do not relax the return objective or turnover limit without committee action.
- Git history for this record: original prediction commit `49716cf`; final pre-run freeze `d463d00ec290be407ac79d26475f29dbfe21b0a7`. The blank pre-run field above is retained unchanged because it is part of the committed Prediction section.
- Post-run commit hash: `bab663c095b1937fa1cf61201ad49fad41e0e2f9`
- Subsequent reporting correction (not part of original locked output): `a0277cb238edb8adeb880b1f70166cea5922c152`.
