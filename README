# Seldon Engine

Seldon Engine is a **personal quantitative research platform** focused on **daily equities and ETF data ingestion**, reproducible storage, and efficient modeling.

The project is intentionally scoped to:
- daily frequency (EOD)
- liquid ETFs (US, international, and Mexican FIBRAs)
- research and education use cases

It is **not** a trading system and does not place orders.

---

## Design Philosophy

1. **Reproducibility over cleverness**  
   Raw data is snapshotted and stored immutably. Derived data can always be recomputed.

2. **Explicit governance**  
   The asset universe is versioned and documented. Changes are deliberate.

3. **Low operational overhead**  
   Embedded analytics (DuckDB), file-based storage (Parquet), and minimal services.

4. **Defensive data engineering**  
   No assumptions about providers. Symbol normalization and schema enforcement are mandatory.

---

## What the system does

- Defines a governed ETF universe (~100 instruments)
- Downloads historical and daily OHLCV data
- Normalizes all providers into a canonical schema
- Stores data as Parquet (local and/or MinIO)
- Enables fast querying via DuckDB
- Runs automatically on a daily schedule (Docker + cron)

---

## Repository Structure

```

.
├── config/
│   └── equities_universe.yaml        # Universe definition + provider mappings
├── ingest/
│   ├── universe.py                   # Universe loading
│   ├── symbols.py                    # Symbol normalization layer
│   └── stooq.py                      # Stooq data client
├── schemas/
│   └── equities_daily.py             # Canonical OHLCV schema
├── scripts/
│   └── ingest_equities_daily.py      # Daily ingestion entrypoint
├── storage/
│   ├── raw/equities_daily/           # Parquet snapshots (partitioned by symbol)
│   └── research.duckdb               # Embedded analytics DB (optional)
├── docker/
│   ├── cron/
│   └── entrypoint.sh
├── Dockerfile
├── docker-compose.yml
└── README.md

```

---

## Canonical Data Schema

All providers are normalized into the following schema:

| Column        | Description                                  |
|--------------|----------------------------------------------|
| date         | Trading date (daily)                          |
| symbol       | Canonical symbol                              |
| open         | Open price                                   |
| high         | High price                                   |
| low          | Low price                                    |
| close        | Close price                                  |
| adj_close    | Adjusted close (nullable)                    |
| volume       | Trading volume                               |
| source       | Data provider (`stooq`, `yahoo`)              |
| ingested_at  | Ingestion timestamp                          |

Schema enforcement is implemented in `schemas/equities_daily.py`.

---

## Asset Universe

- Liquid US ETFs (broad market, sectors, factors)
- Fixed income ETFs
- Commodity ETFs
- Crypto-linked ETFs (e.g. spot BTC ETFs)
- Mexican FIBRAs (BMV-listed REIT-like vehicles)

The universe is defined and governed in:

```

config/equities_universe.yaml

````

Provider-specific symbol mappings are explicit and externalized.

---

## Data Providers

### Primary
- **Stooq** (CSV endpoints, no official API)

### Secondary (fallback, optional)
- Yahoo Finance

Stooq is treated as a **public data dump**, not a guaranteed API. All data is cached locally.

---

## Storage Model

### Raw data
- Parquet files
- Partitioned by symbol
- Append-only, immutable snapshots

### Analytics
- DuckDB (embedded, file-based)
- Reads Parquet directly
- No database server required

This design supports interactive research without cluster infrastructure.

---

## Running locally (without Docker)

```bash
pip install -r requirements.txt
python -m scripts.ingest_equities_daily
````

Query with DuckDB:

```python
import duckdb

con = duckdb.connect("storage/research.duckdb")
df = con.execute("""
  SELECT symbol, max(date) AS last_date
  FROM read_parquet('storage/raw/equities_daily/symbol=*/part-*.parquet')
  GROUP BY symbol
  ORDER BY symbol
""").df()
```

---

## Running with Docker (recommended)

### Start services

```bash
docker compose up -d --build
```

This starts:

* `app` – Python ingestion service with cron
* `minio` – S3-compatible object storage
* `minio-init` – bucket bootstrap

### Daily schedule

By default, ingestion runs **daily at 02:10 (local time)**.

To change the schedule, edit:

```yaml
CRON_SCHEDULE: "10 2 * * *"
```

in `docker-compose.yml`.

### MinIO Console

* URL: [http://localhost:9001](http://localhost:9001)
* Default credentials:

  * user: `minio`
  * password: `minio12345`

---

## Why DuckDB and not Spark?

* Dataset size: small to medium (daily bars, ~100 ETFs)
* Single-user research
* Interactive modeling

DuckDB provides:

* Direct Parquet reads
* Vectorized execution
* SQL + Python API
* Zero operational overhead

Spark/MinIO is intentionally avoided at this stage.

---

## What this is NOT

* Not a trading system
* Not a backtesting engine (yet)
* Not production market data infrastructure

This is a **research platform**.

---

## Roadmap (intentionally incremental)

* Provider fallback and retry logic
* Ingestion manifest and monitoring
* Liquidity filters (ADV-based)
* Derived datasets (returns, volatility, factors)
* Backtesting layer
* Portfolio construction and risk models

---

## Disclaimer

This project is for **research and educational purposes only**.
Data sources may be unofficial and incomplete.
Do not rely on this system for live trading or financial decisions.

---

## Name Origin

“Seldon Engine” references Isaac Asimov’s *Foundation* series — a symbolic device for modeling large-scale systems under uncertainty.