# Project 2 data card

## Portfolio-price input

| Field | Record |
| --- | --- |
| File | [`prices.csv`](../prices.csv) at repository root; model reads it without alteration. |
| Intended columns | `Date,BIL,IEF,AGG,ACWI` |
| Intended coverage | 60 monthly labels, October 2021–September 2026 (59 returns) |
| Source / URLs | [`Project-2-Data-Sources.md`](../Project-2-Data-Sources.md), preserving the four Yahoo Finance chart URLs verbatim. |
| Documented download date | October 22, 2026. |
| Cutoff | September 2026 period label; no later observation may enter without a documented cutoff change. |
| Checks | Exact schema/window; unique chronological month labels; no missing cells; finite positive prices; matching ticker definitions. |
| Preservation | The model reads CSV only and never overwrites it. |

Date labels are monthly periods, not confirmed publication or trade-availability timestamps. They should not be used to claim a historical intraday or exact as-of signal.

## Signal data card

| Field | Record |
| --- | --- |
| Source | The same validated bundled CSV; no live download. |
| Observation period | Monthly labels through the user-selected decision cutoff. |
| Signal | N-month trailing price return: latest eligible price / price N months earlier − 1; default N=12. |
| Availability assumption | A label is considered eligible only if its date is on/before the selected cutoff. This is a conservative software filter, not proof of vendor publication time. |
| Transformations | Price levels to simple returns; no winsorization, imputation, or silent repair. |
| Missing handling | Any missing/invalid price stops the application. |
| Decision relevance | Monitoring input for whether an allocation pilot needs review; it does not mechanically override mandate constraints. |
| Limitations | Yahoo adjusted-price publication timestamps are not available in this repository. Historical signal claims therefore require a separately sourced availability record. |

The ACWI–AGG correlation stress is a model-assumption adjustment around each estimation window's own historical correlation. The 59- and 36-return covariances are validated independently; an invalid covariance is not repaired or used.

## Economic sanity check

The Lab 16 gate establishes what could have been known, not whether it is economically credible. A provenance-valid observation that implies a large unexplained one-month price movement still requires source, units, corporate-action, and market-plausibility review before it affects a decision.

**Concrete teaching example — not portfolio input:** suppose a validly published ETF observation moves from $100 to $1,500 in one month, implying a +1,400% simple return, with no documented split, distribution adjustment, currency/unit change, or market event. It can pass the provenance gate because it was available by the decision date, yet it is economically implausible enough to quarantine pending source and corporate-action review. This example does not alter `prices.csv`, the signal, or any portfolio result.
