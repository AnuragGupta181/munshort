"""Clean and normalize raw scraped data."""

import json
import re
from pathlib import Path

import pandas as pd


def load_raw_data(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load all raw JSON files into DataFrames."""
    all_products = []
    all_reviews = []

    for f in raw_dir.glob("*_products.json"):
        with open(f) as fh:
            all_products.extend(json.load(fh))

    for f in raw_dir.glob("*_reviews.json"):
        with open(f) as fh:
            all_reviews.extend(json.load(fh))

    products_df = pd.DataFrame(all_products) if all_products else pd.DataFrame()
    reviews_df = pd.DataFrame(all_reviews) if all_reviews else pd.DataFrame()

    return products_df, reviews_df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize product data."""
    if df.empty:
        return df

    # Deduplicate by ASIN
    df = df.drop_duplicates(subset="asin", keep="first")

    # Normalize brand names
    df["brand"] = df["brand"].str.strip().str.title()

    # Remove products with no price
    df = df[df["price"] > 0].copy()

    # Ensure list_price >= price
    df.loc[df["list_price"] < df["price"], "list_price"] = df["price"]

    # Compute discount percentage
    df["discount_pct"] = ((1 - df["price"] / df["list_price"]) * 100).round(1)
    df.loc[df["list_price"] == df["price"], "discount_pct"] = 0.0

    # Fill missing ratings
    df["rating"] = df["rating"].fillna(0.0)
    df["review_count"] = df["review_count"].fillna(0).astype(int)

    return df.reset_index(drop=True)


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize review data."""
    if df.empty:
        return df

    # Remove empty reviews
    df = df[df["body"].str.len() > 5].copy()

    # Normalize brand
    df["brand"] = df["brand"].str.strip().str.title()

    # Clean date - try to parse various formats
    def parse_date(date_str):
        if not date_str or not isinstance(date_str, str):
            return ""
        # Amazon format: "Reviewed in India on 15 March 2024"
        match = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", date_str)
        if match:
            try:
                return pd.to_datetime(match.group(1), format="mixed").strftime("%Y-%m-%d")
            except Exception:
                pass
        return date_str

    df["date"] = df["date"].apply(parse_date)

    # Ensure rating is int
    df["rating"] = df["rating"].fillna(0).astype(int)
    df["helpful_votes"] = df["helpful_votes"].fillna(0).astype(int)
    df["verified"] = df["verified"].fillna(False)

    return df.reset_index(drop=True)
