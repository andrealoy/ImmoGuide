# core/viz/stats.py
import pandas as pd


def basic_stats(df):
    return {
        "count": int(len(df)),
        "median": float(df["price_m2"].median()),
        "mean": float(df["price_m2"].mean()),
    }


def weekly_median(df, city, date_col):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)

    df["week"] = df[date_col].dt.to_period("W").apply(lambda r: r.start_time)

    weekly = (
        df.groupby("week")["price_m2"]
        .median()
        .reset_index(name="median_price_m2")
    )

    weekly["city"] = city

    weekly["smooth"] = (
        weekly["median_price_m2"]
        .rolling(window=3, center=True, min_periods=1)
        .median()
    )

    return weekly
