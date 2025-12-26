from pathlib import Path
import pandas as pd

from ingest.universe import load_universe_config, extract_canonical_symbols
from ingest.symbols import build_stooq_map_from_config
from ingest.stooq import StooqClient, fetch_stooq_daily
from schemas.equities_daily import enforce_equities_daily_schema

RAW_ROOT = Path("storage/raw/equities_daily")

def load_existing_symbol(symbol: str) -> pd.DataFrame | None:
    path = RAW_ROOT / f"symbol={symbol}"
    if not path.exists():
        return None
    files = list(path.glob("*.parquet"))
    if not files:
        return None
    return pd.read_parquet(path)

def write_symbol_partition(df: pd.DataFrame) -> None:
    symbol = df["symbol"].iloc[0]
    path = RAW_ROOT / f"symbol={symbol}"
    path.mkdir(parents=True, exist_ok=True)
    out_file = path / f"part-{pd.Timestamp.utcnow().strftime('%Y%m%dT%H%M%S')}.parquet"
    df.to_parquet(out_file, index=False)

def merge_dedupe(existing: pd.DataFrame | None, new: pd.DataFrame) -> pd.DataFrame:
    if existing is None or existing.empty:
        return new
    combined = pd.concat([existing, new], ignore_index=True)
    combined = combined.sort_values(["date", "source", "ingested_at"])
    # keep latest ingested row for same date/source
    combined = combined.drop_duplicates(subset=["date", "source"], keep="last")
    combined = combined.sort_values("date")
    return enforce_equities_daily_schema(combined)

def main():
    cfg = load_universe_config("config/equities_universe.yaml")
    canonical_symbols = extract_canonical_symbols(cfg)

    stooq_map = build_stooq_map_from_config(cfg)
    client = StooqClient()

    RAW_ROOT.mkdir(parents=True, exist_ok=True)

    for sym in canonical_symbols:
        stooq_sym = stooq_map.to_provider(sym)
        print(f"[stooq] fetching {sym} ({stooq_sym}) ...")

        new_df = fetch_stooq_daily(client, stooq_symbol=stooq_sym, canonical_symbol=sym)

        existing = load_existing_symbol(sym)
        merged = merge_dedupe(existing, new_df)

        # Rewrite: simplest approach for now (one symbol partition directory)
        # For larger scale later: maintain a single consolidated parquet and incremental append logic.
        # Here we write a new part file; downstream reads can concat.
        write_symbol_partition(merged)
        print(f"  -> {sym}: {len(merged)} rows stored")

if __name__ == "__main__":
    main()
