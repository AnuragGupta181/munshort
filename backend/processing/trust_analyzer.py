"""Analyze review trust signals."""

import pandas as pd


def analyze_trust(products: list[dict], reviews: list[dict]) -> list[dict]:
    """Compute trust signals for each product."""
    reviews_df = pd.DataFrame(reviews) if reviews else pd.DataFrame()
    signals = []

    for product in products:
        asin = product.get("asin", "")
        prod_reviews = reviews_df[reviews_df["product_asin"] == asin] if not reviews_df.empty else pd.DataFrame()

        if prod_reviews.empty:
            signals.append({
                "asin": asin,
                "brand": product.get("brand", ""),
                "product_title": product.get("title", ""),
                "trust_score": 50.0,
                "verified_ratio": 0.0,
                "five_star_ratio": 0.0,
                "avg_review_length": 0,
                "total_reviews": 0,
                "flags": ["No reviews to analyze"],
            })
            continue

        total = len(prod_reviews)
        verified_count = int(prod_reviews["verified"].sum()) if "verified" in prod_reviews.columns else 0
        verified_ratio = verified_count / total * 100
        five_star_count = int((prod_reviews["rating"] == 5).sum())
        five_star_ratio = five_star_count / total * 100
        avg_length = float(prod_reviews["body"].str.len().mean()) if "body" in prod_reviews.columns else 0

        # Compute trust score (0-100)
        trust_score = 70.0  # Base score

        # Verified purchase ratio (higher is better)
        if verified_ratio >= 80:
            trust_score += 10
        elif verified_ratio < 50:
            trust_score -= 15

        # Five-star distribution (too many 5-stars is suspicious)
        if five_star_ratio > 85:
            trust_score -= 20
        elif five_star_ratio > 70:
            trust_score -= 10
        elif 30 <= five_star_ratio <= 60:
            trust_score += 5

        # Review length (very short reviews are suspicious)
        if avg_length < 30:
            trust_score -= 15
        elif avg_length > 100:
            trust_score += 10

        # Review count
        if total < 3:
            trust_score -= 10
        elif total > 20:
            trust_score += 5

        trust_score = max(0, min(100, trust_score))

        flags = []
        if five_star_ratio > 80:
            flags.append("Unusually high 5-star ratio")
        if verified_ratio < 50:
            flags.append("Low verified purchase ratio")
        if avg_length < 30:
            flags.append("Very short average review length")

        # Check for review bursts (many reviews on same date)
        if "date" in prod_reviews.columns:
            date_counts = prod_reviews["date"].value_counts()
            if len(date_counts) > 0 and date_counts.iloc[0] >= 5:
                flags.append("Suspicious review burst detected")
                trust_score -= 10

        trust_score = max(0, min(100, trust_score))

        signals.append({
            "asin": asin,
            "brand": product.get("brand", ""),
            "product_title": product.get("title", ""),
            "trust_score": round(trust_score, 1),
            "verified_ratio": round(verified_ratio, 1),
            "five_star_ratio": round(five_star_ratio, 1),
            "avg_review_length": round(avg_length),
            "total_reviews": total,
            "flags": flags,
        })

    return signals
