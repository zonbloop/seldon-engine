# ingest/stooq.py
from __future__ import annotations
import io
import time
from dataclasses import dataclass
from typing import Optional
import pandas as pd
import requests

from schemas.equities_daily import enforce_equities_daily_schema, validate_no_duplicates

STOOQ_DAILY_URL = "https://stooq.com/q/d/l/"

@dataclass
class StooqClient:
    timeout_s: int = 30
    max_retries: int = 4
    backoff_s: float = 1.5
    user_agent: str = "prime-radiant/0.1 (research)"

    def fetch_daily_csv(self, stooq_symbol: str) -> str:
        params = {"s": stooq_symbol, "i": "d"}
        headers = {"User-Agent": self.user_agent}

        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                r = requests.get(STOOQ_DAILY_URL, params=params, headers=headers, timeout=self.timeout_s)
                r.raise_for_status()
                text = r.text
                # Basic sanity: must have header row
                if "Date,Open,High,Low,Close,Volume" not in text:
                    raise ValueError(f"Unexpected CSV header for {stooq_symbol}")
                return text
            except Exception as e:
                last_err = e
                time.sleep(self.backoff_s * (attempt + 1))
        raise RuntimeError(f"Failed to fetch Stooq data for {stooq_symbol}") from last_err

def parse_stooq_daily_csv(
    csv_text: str,
    canonical_symbol: str,
    source: str = "stooq",
    ingested_at: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    if ingested_at is None:
        ingested_at = pd.Timestamp.utcnow()

    raw = pd.read_csv(io.StringIO(csv_text))
    # Expected: Date,Open,High,Low,Close,Volume
    raw = raw.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })

    raw["symbol"] = canonical_symbol
    raw["adj_close"] = pd.NA  # Stooq daily endpoint typically does not provide adj close
    raw["source"] = source
    raw["ingested_at"] = ingested_at

    df = enforce_equities_daily_schema(raw)
    validate_no_duplicates(df)
    return df

def fetch_stooq_daily(
    client: StooqClient,
    stooq_symbol: str,
    canonical_symbol: str,
) -> pd.DataFrame:
    csv_text = client.fetch_daily_csv(stooq_symbol)
    return parse_stooq_daily_csv(csv_text, canonical_symbol=canonical_symbol)