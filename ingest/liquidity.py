import pandas as pd

#    Computes rolling ADV (dollar volume) per symbol.
#    Expects canonical columns: ['symbol','date', price_col, volume_col]
def compute_adv(
    df: pd.DataFrame,
    window: int = 63,
    price_col: str = "close",
    volume_col: str = "volume",
) -> pd.Series:
    df = df.sort_values(["symbol", "date"])
    dollar_vol = df[price_col].astype("float64") * df[volume_col].astype("float64")
    return dollar_vol.groupby(df["symbol"]).rolling(window).median().reset_index(level=0, drop=True)

def liquidity_filter_adv(
    df: pd.DataFrame,
    window: int = 63,
    min_adv_usd: float = 5_000_000.0,
    min_history_days: int = 252,
    min_nonzero_volume_ratio: float = 0.98,
) -> pd.DataFrame:
    df = df.sort_values(["symbol", "date"]).copy()
    df["dollar_volume"] = df["close"].astype("float64") * df["volume"].astype("float64")

    # history length
    hist = df.groupby("symbol").size().rename("n_days")

    # nonzero volume ratio
    nonzero_ratio = (df["volume"] > 0).groupby(df["symbol"]).mean().rename("nonzero_volume_ratio")

    # ADV on last date available per symbol (rolling median)
    df["adv"] = df.groupby("symbol")["dollar_volume"].rolling(window).median().reset_index(level=0, drop=True)
    last_adv = df.groupby("symbol")["adv"].tail(1).set_axis(df.groupby("symbol").tail(1)["symbol"]).rename("adv_last")

    out = pd.concat([hist, nonzero_ratio, last_adv], axis=1).reset_index().rename(columns={"index": "symbol"})
    out["pass_history"] = out["n_days"] >= min_history_days
    out["pass_nonzero_volume"] = out["nonzero_volume_ratio"] >= min_nonzero_volume_ratio
    out["pass_adv"] = out["adv_last"] >= min_adv_usd
    out["pass_liquidity"] = out["pass_history"] & out["pass_nonzero_volume"] & out["pass_adv"]
    return out.sort_values(["pass_liquidity", "adv_last"], ascending=[False, False])