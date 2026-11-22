"""Point-in-time provenance filters and an intentionally small teaching fixture."""
from __future__ import annotations
from datetime import date
import pandas as pd


def provenance_gate(rows: pd.DataFrame, decision_date: str | pd.Timestamp) -> pd.DataFrame:
    required = {"row_id", "ticker", "observation_date", "published_at", "value"}
    if not required.issubset(rows.columns):
        raise ValueError(f"Missing provenance fields: {sorted(required - set(rows.columns))}")
    try:
        frame = rows.copy(deep=True).assign(
            observation_date=rows["observation_date"].map(lambda x: date.fromisoformat(str(x))),
            published_at=rows["published_at"].map(lambda x: date.fromisoformat(str(x))),
        )
        cutoff = date.fromisoformat(str(decision_date)[:10])
    except (TypeError, ValueError):
        raise ValueError("Provenance dates must use ISO YYYY-MM-DD format.")
    frame = frame.dropna(subset=["ticker"])
    frame = frame[frame["ticker"].astype(str).str.strip() != ""]
    frame = frame.drop_duplicates(subset=["ticker", "observation_date", "published_at", "value"])
    frame = frame[frame["published_at"] <= cutoff]
    return (frame.sort_values(["ticker", "observation_date", "published_at", "row_id"])
            .groupby(["ticker", "observation_date"], as_index=False).tail(1)
            .sort_values("row_id").reset_index(drop=True))


def trailing_signals(rows: pd.DataFrame) -> pd.Series:
    ordered = rows.sort_values(["ticker", "observation_date"])
    def calc(group: pd.DataFrame) -> float:
        if len(group) < 2: return float("nan")
        return group.iloc[-1]["value"] / group.iloc[0]["value"] - 1
    return ordered.groupby("ticker").apply(calc, include_groups=False)


def fictional_lab16_rows() -> pd.DataFrame:
    # IDs 1,4,5,6,9,12 survive on 2026-03-15. Later revisions make naive returns wrong.
    return pd.DataFrame([
        (1,"AAA","2026-01-31","2026-02-01",100.00), (2,"AAA","2026-01-31","2026-02-01",100.00),
        (3,"AAA","2026-02-28","2026-03-20",105.83), (4,"AAA","2026-02-28","2026-03-01",101.98),
        (5,"BBB","2026-01-31","2026-02-01",100.00), (6,"BBB","2026-02-28","2026-03-01",98.98),
        (7,"BBB","2026-02-28","2026-03-20",94.85), (8,"","2026-02-28","2026-03-01",99.00),
        (9,"CCC","2026-01-31","2026-02-01",100.00), (10,"CCC","2026-02-28","2026-03-20",101.82),
        (11,None,"2026-02-28","2026-03-01",100.00), (12,"CCC","2026-02-28","2026-03-01",100.91),
    ], columns=["row_id","ticker","observation_date","published_at","value"])


def lab16_known_answers() -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    rows = fictional_lab16_rows()
    retained = provenance_gate(rows, "2026-03-15")
    # Deliberately naive: it removes missing tickers but uses the latest revision
    # regardless of its publication date.  This isolates look-ahead bias.
    naive = rows.dropna(subset=["ticker"]).copy()
    naive = naive[naive["ticker"].astype(str).str.strip() != ""]
    naive = naive.assign(
        observation_date=naive["observation_date"].map(lambda x: date.fromisoformat(str(x))),
        published_at=naive["published_at"].map(lambda x: date.fromisoformat(str(x))),
    )
    naive = (naive.sort_values(["ticker", "observation_date", "published_at", "row_id"])
                  .groupby(["ticker", "observation_date"], as_index=False).tail(1))
    return trailing_signals(retained), trailing_signals(naive), retained
