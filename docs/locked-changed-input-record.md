# Locked Changed-Input Record — Human AI-off section required

**Do not run the changed-input test until you have completed the Prediction section with AI closed and committed this file to GitHub. Do not edit the prediction afterward.**

## Prediction (complete yourself, with AI off)

Date/time: 11/22/2026
Final-engine file and command to be run: run_model.py — python3 run_model.py --reserve-minimum 0.30 --output output/locked-reserve-minimum-030.json
Input changed (old value, new value, units): Minimum BIL reserve allocation increases from 3% to 30% of the portfolio. All other inputs remain unchanged.
Expected direction of weights/return/volatility/turnover/decision: I expect the portfolio to increase its BIL allocation from 25% to at least 30%. This will leave less room for the other investments, so I expect the optimizer to reduce one or more of those positions. BIL is a lower-risk investment, and I expect volatility to decrease, although the estimated return may also decline. Turnover could increase because the portfolio has to adjust to the higher reserve requirement. I am less certain whether the model will still meet its return and turnover constraints.
Why (model constraint or assumption): The optimizer must satisfy the minimum reserve requirement while also meeting its return objective and other portfolio restrictions. Raising the BIL minimum above the current allocation makes the constraint more restrictive and could force the model to sacrifice return or change its allocation.
Expected committee action and reversal condition: I expect the committee's current STOP recommendation to remain in place because the original portfolio already showed sensitivity to the estimation window. I would reconsider that decision if the revised portfolio satisfies the mandate, remains stable under the required stress tests, and resolves the outstanding compliance checks.

Pre-run commit hash: To be added to the validation record after committing this prediction.

## Execute only after the pre-run commit

- Command:
- Output file/location:
- Observed change (with units):
- Comparison to prediction:
- First broken assumption/unit/sign/date/interface if prediction differed:
- Final action: `ACTION HOLDS`, `ACTION CHANGES`, or `EVIDENCE INSUFFICIENT`:
- Post-run commit hash:
