"""Detect anomalies in product/review data."""


def detect_anomalies(products: list[dict], reviews: list[dict]) -> list[dict]:
    """Detect various anomalies across products and reviews."""
    anomalies = []

    for product in products:
        asin = product.get("asin", "")
        brand = product.get("brand", "")
        title = product.get("title", "")
        rating = product.get("rating", 0)
        sentiment = product.get("sentiment_score", 0)
        discount = product.get("discount_pct", 0)

        # High rating but negative sentiment
        if rating >= 4.0 and sentiment < 0.0:
            anomalies.append({
                "type": "sentiment_rating_divergence",
                "severity": "warning",
                "brand": brand,
                "product_title": title,
                "description": (
                    f"Product has {rating} stars but sentiment score is {sentiment:.2f}. "
                    f"Reviews suggest quality concerns despite high rating."
                ),
            })

        # Suspicious pricing (very high discount)
        if discount > 55:
            anomalies.append({
                "type": "suspicious_pricing",
                "severity": "info",
                "brand": brand,
                "product_title": title,
                "description": (
                    f"Discount of {discount:.0f}% (₹{product.get('list_price', 0)} → ₹{product.get('price', 0)}) "
                    f"suggests potentially inflated list price."
                ),
            })

        # Durability complaints in high-rated products
        aspects = product.get("aspects", {})
        durability = aspects.get("durability", 0)
        if rating >= 4.0 and durability < -0.1:
            anomalies.append({
                "type": "durability_concern",
                "severity": "critical",
                "brand": brand,
                "product_title": title,
                "description": (
                    f"Despite {rating} star rating, durability aspect sentiment is {durability:.2f}. "
                    f"Customers report breakage/damage issues."
                ),
            })

        # Low trust score with high rating
        trust = product.get("trust_score", 100)
        if trust < 50 and rating >= 4.0:
            anomalies.append({
                "type": "trust_concern",
                "severity": "warning",
                "brand": brand,
                "product_title": title,
                "description": (
                    f"Product has {rating} stars but trust score is only {trust:.0f}/100. "
                    f"Review authenticity may be questionable."
                ),
            })

    # Sort by severity (critical first)
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    anomalies.sort(key=lambda a: severity_order.get(a["severity"], 3))

    return anomalies[:20]
