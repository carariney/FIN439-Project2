# Meridian Foundation — Committee Decision Memo

AI tools used: OpenAI Codex assisted with code structure, tests, and documentation; it did not generate or download market observations.

The analysis and decision are mine, for education rather than investment advice.

## Recommendation: defer immediate adoption; seek a committee decision before any pilot

**Authorized implementation range: 0% pending committee approval.** This is a decision boundary, not an estimate of an optimal allocation. The model's 25% BIL / 20% AGG / 55% ACWI turnover-constrained candidate is a diagnostic result only and is not an authorized implementation range.

The proposed process is a transparent 5%-increment, long-only minimum-volatility search across BIL, IEF, AGG, and ACWI, subject to a reserve floor, modeled return threshold, and the 25% one-way turnover limit from the documented 60% ACWI / 40% AGG starting portfolio. The bundled price file and source record support reproducible estimates, but the resulting allocation is not a committee-ready recommendation because material mandate rules remain unverified.

The original unconstrained result, 60% BIL / 40% ACWI, is retained only as a comparison. It requires 60% one-way turnover and therefore exceeds the 25% limit absent committee approval. It makes immediate adoption inappropriate. Under the same 6.5% proxy target and five-percentage-point grid, the turnover-constrained result is 25% BIL / 20% AGG / 55% ACWI, with 25% one-way turnover. It is a modeled result, not a recommended or approved pilot allocation. A committee exception is not justified by the model alone: it would require explicit approval of the turnover breach, the optimization objective, liquidity/issuer evidence, and the unresolved loss rule.

The estimation-window guardrail currently stops the process: the 36-return version is 25% BIL / 40% AGG / 35% ACWI, a 20-percentage-point maximum allocation difference from the 59-return result. The documented stopping threshold is a change of at least 20 percentage points. This sensitivity means neither a turnover-compliant pilot nor a turnover exception is justified by this output alone.

The IPS requires a seven-year horizon; CPI + 4% annualized net of costs evaluated over rolling five-year periods; a 3% reserve; the 60/40 global-equity/U.S.-investment-grade-bond reference benchmark; long-only/no borrowing, shorts, or derivatives; an 8% combined nonexempt-issuer cap; 25% annual turnover without approval; and 90% redeemability in five business days. The calendar-year loss rule is unresolved. The policy has not yet approved optimization priority. Minimizing estimated volatility subject to a return objective is therefore an implementation proposal, not current policy.

The 6.5% Lab 15 training target is only a proxy: it equals a displayed 2.5% inflation assumption plus 4%, not a substitution for actual CPI + 4%. Historical averages are estimates, not reliable forecasts, and cannot demonstrate five-year net achievement.

## Conditions, monitoring, and reversal

Before any pilot, preserve a checksum of the original 60-row CSV and October 22, 2026 source record; obtain CIO definitions for loss measurement and optimization priority; document ETF liquidity/redemption and issuer-exemption evidence; approve the stated starting weights, turnover convention, and one-time transaction-cost assumption; and review the completed locked changed-input evidence, which found the 30% reserve case infeasible under the modeled return and turnover constraints.

Monitor each rebalance for reserve below 3%, one-way turnover above 25%, an infeasible target, covariance validation failure, a largest allocation change of at least 20 percentage points between the 36- and 59-return windows, or a signal/data-provenance exception. The cost display treats costs as one-time implementation costs and separately shows a five-year annualized cost-drag proxy; it does not subtract the cost every year. Suspend the process on any infeasible turnover-constrained optimization, modeled hard-rule FAIL, missing or revised provenance evidence, or material instability. Reverse a pilot only under a separately documented committee instruction; the model does not authorize trading. **Committee ask:** confirm the 0% implementation range pending resolution of the listed evidence gaps and either define the additional conditions for a future pilot or formally reject the process.
