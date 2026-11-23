# FIN 439 Project 2 — Final Preflight Report

Audit date: 2026-11-23

## Verification completed

- `python3 -m pytest -q`: 15 passed. The test suite compares the current default calculation in memory with the frozen baseline without rewriting it.
- Streamlit reached its local-server startup message using `python3 -m streamlit run app.py --server.headless true --server.port 8502`.
- `prices.csv` contains 60 observations (October 2021–September 2026) and SHA-256 `df1ca3ff8e9f4f12680adbb1dce73fd8e9cd61775bddde4cd93b26e57b6aa876`, matching the documented checksum.
- Neither protected JSON file has a working-tree diff. The locked 30% command was not rerun.
- The `Prediction` block has not changed since the final pre-run freeze. Git history orders the prediction commit (`49716cf`), final pre-run freeze (`d463d00`), and post-run evidence (`bab663c`) in that order.
- The baseline output, memo, data card, README, and app agree on the documented constraints and STOP boundary: BIL-only reserve eligibility; 3% baseline reserve; 25% one-way turnover cap; 6.5% proxy target; 25% BIL / 20% AGG / 55% ACWI modeled candidate; 20-percentage-point 36-versus-59-return instability; and 0% authorized implementation pending committee approval. Historical estimates and forecast overrides are distinctly labelled.

## Corrections made

- Removed the obsolete pre-run instruction outside the frozen `Prediction` block from `docs/locked-changed-input-record.md`.
- Removed the stale pending-checksum item from `docs/validation-and-ai-use.md`; the same file records the verified SHA-256 checksum.

## Remaining issues

### BLOCKER

- `docs/submission-manifest.md:20`
- `docs/submission-manifest.md:21`
- `docs/submission-manifest.md:22`
- `docs/submission-manifest.md:23`

  All three video rows still have pending URLs, durations, transcripts, timestamp indexes, and logged-out access checks; the submission receipt is also pending. These are not present in the repository and were not fabricated or externally verified.

No unresolved code, numerical-consistency, reproducibility-instruction, or frozen-artifact issue was found in this audit.
