"""Pricing analysis: price bands, discount patterns, spreads."""

import pandas as pd


def analyze_pricing(products_df: pd.DataFrame) -> dict:
    """Compute pricing metrics per brand."""
    if products_df.empty:
        return {}

    brand_stats = []
    all_prices = products_df["price"].values

    # Compute quartile boundaries for price bands
    q25 = float(products_df["price"].quantile(0.25))
    q50 = float(products_df["price"].quantile(0.50))
    q75 = float(products_df["price"].quantile(0.75))

    for brand, group in products_df.groupby("brand"):
        avg_price = float(group["price"].mean())

        if avg_price <= q25:
            price_band = "budget"
        elif avg_price <= q50:
            price_band = "value"
        elif avg_price <= q75:
            price_band = "midrange"
        else:
            price_band = "premium"

        brand_stats.append({
            "brand": brand,
            "avg_price": round(avg_price),
            "median_price": round(float(group["price"].median())),
            "min_price": int(group["price"].min()),
            "max_price": int(group["price"].max()),
            "price_std": round(float(group["price"].std()), 1),
            "avg_discount": round(float(group["discount_pct"].mean()), 1),
            "median_discount": round(float(group["discount_pct"].median()), 1),
            "product_count": len(group),
            "price_band": price_band,
            "discount_dependent": float(group["discount_pct"].mean()) > 40,
        })

    return {
        "brand_pricing": brand_stats,
        "quartiles": {"q25": q25, "q50": q50, "q75": q75},
        "overall_avg_price": round(float(all_prices.mean())),
    }
