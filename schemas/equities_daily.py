from dataclasses import dataclass
from typing import Final, List
import pandas as pd

CANON_COLS: Final[List[str]] = [
    "date",        # datetime64[ns] normalized to date boundary (UTC naive is fine for daily)
    "symbol",      # canonical symbol string
    "open",
    "high",
    "low",
    "close",
    "adj_close",   # nullable float
    "volume",
    "source",      # 'stooq' or 'yahoo'
    "ingested_at", # timestamp
]

DTYPES: Final[dict] = {
    "symbol": "string",
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "adj_close": "float64",
    "volume": "float64",
    "source": "string",
}

def enforce_equities_daily_schema(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in CANON_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df[CANON_COLS].copy()

    # date normalization
    out["date"] = pd.to_datetime(out["date"], utc=False).dt.normalize()

    # ingested_at as timestamp
    out["ingested_at"] = pd.to_datetime(out["ingested_at"], utc=False)

    # dtypes
    for col, dtype in DTYPES.items():
        out[col] = out[col].astype(dtype)

    return out

def validate_no_duplicates(df: pd.DataFrame) -> None:
    dup = df.duplicated(subset=["symbol", "date", "source"]).any()
    if dup:
        raise ValueError("Duplicate rows detected for (symbol,date,source).")