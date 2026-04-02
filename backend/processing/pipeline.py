"""Orchestrates the full data processing pipeline."""

import json
from pathlib import Path

from backend.processing.data_cleaner import load_raw_data, clean_products, clean_reviews
from backend.processing.pricing_analyzer import analyze_pricing
from backend.processing.sentiment_analyzer import analyze_all_reviews, generate_review_synthesis
from backend.processing.aspect_extractor import extract_aspects_for_product, compute_brand_aspects
from backend.processing.anomaly_detector import detect_anomalies
from backend.processing.trust_analyzer import analyze_trust
from backend.processing.insights_generator import generate_insights


BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def run_pipeline(force: bool = False, skip_llm: bool = False):
    """Run the full processing pipeline."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load and clean data
    print("Step 1: Loading and cleaning raw data...")
    products_df, reviews_df = load_raw_data(RAW_DIR)

    if products_df.empty:
        print("  No raw data found. Run the scraper first: uv run python scripts/scrape.py all")
        return

    products_df = clean_products(products_df)
    reviews_df = clean_reviews(reviews_df)
    print(f"  Loaded {len(products_df)} products, {len(reviews_df)} reviews")

    # Step 2: Pricing analysis
    print("\nStep 2: Analyzing pricing...")
    pricing = analyze_pricing(products_df)
    brand_pricing = {bp["brand"]: bp for bp in pricing.get("brand_pricing", [])}

    # Step 3: Sentiment analysis
    print("\nStep 3: Running sentiment analysis...")
    reviews_list = reviews_df.to_dict("records")
    if not skip_llm:
        reviews_list = analyze_all_reviews(reviews_list)
    else:
        # Fallback: rating-based sentiment
        for r in reviews_list:
            rating = r.get("rating", 3)
            r["sentiment_score"] = (rating - 3) / 2.5
            r["sentiment_label"] = (
                "very_positive" if r["sentiment_score"] > 0.5
                else "positive" if r["sentiment_score"] > 0.1
                else "neutral" if r["sentiment_score"] > -0.1
                else "negative" if r["sentiment_score"] > -0.5
                else "very_negative"
            )
            r["aspects_mentioned"] = []

    # Step 4: Aspect extraction
    print("\nStep 4: Extracting aspect sentiments...")
    products_list = products_df.to_dict("records")
    brand_product_aspects: dict[str, list] = {}

    for product in products_list:
        asin = product["asin"]
        brand = product["brand"]
        prod_reviews = [r for r in reviews_list if r.get("product_asin") == asin]

        if not skip_llm and prod_reviews:
            aspects = extract_aspects_for_product(prod_reviews)
        else:
            aspects = {a: 0.0 for a in ["wheels", "handle", "material", "zipper", "size_space", "durability"]}

        product["aspects"] = aspects
        brand_product_aspects.setdefault(brand, []).append(aspects)

    # Compute brand-level aspects
    brand_aspects = {
        brand: compute_brand_aspects(product_aspects_list)
        for brand, product_aspects_list in brand_product_aspects.items()
    }

    # Step 5: Generate review synthesis per product
    print("\nStep 5: Generating review syntheses...")
    for product in products_list:
        asin = product["asin"]
        brand = product["brand"]
        prod_reviews = [r for r in reviews_list if r.get("product_asin") == asin]

        if not skip_llm and prod_reviews:
            product["review_synthesis"] = generate_review_synthesis(prod_reviews, brand)
        else:
            product["review_synthesis"] = f"Based on {len(prod_reviews)} reviews."

        # Compute product sentiment as average of review sentiments
        if prod_reviews:
            product["sentiment_score"] = round(
                sum(r.get("sentiment_score", 0) for r in prod_reviews) / len(prod_reviews), 2
            )
        else:
            product["sentiment_score"] = 0.0

        product["review_count"] = len(prod_reviews)
        product["complaint_themes"] = []
        product["appreciation_themes"] = []
        for r in prod_reviews:
            if r.get("sentiment_score", 0) < -0.2:
                product["complaint_themes"].extend(r.get("aspects_mentioned", []))
            elif r.get("sentiment_score", 0) > 0.2:
                product["appreciation_themes"].extend(r.get("aspects_mentioned", []))

        product["complaint_themes"] = list(set(product["complaint_themes"]))[:5]
        product["appreciation_themes"] = list(set(product["appreciation_themes"]))[:5]

    # Step 6: Trust analysis
    print("\nStep 6: Analyzing trust signals...")
    trust_signals = analyze_trust(products_list, reviews_list)
    trust_map = {t["asin"]: t["trust_score"] for t in trust_signals}
    for product in products_list:
        product["trust_score"] = trust_map.get(product["asin"], 50.0)
        product.setdefault("category", "")
        product.setdefault("size", "")

    # Step 7: Build brand summaries
    print("\nStep 7: Building brand summaries...")
    brand_summaries = []
    brands = sorted(set(p["brand"] for p in products_list))

    for brand in brands:
        bp = [p for p in products_list if p["brand"] == brand]
        br = [r for r in reviews_list if r["brand"] == brand]
        pricing_data = brand_pricing.get(brand, {})

        avg_sentiment = sum(r.get("sentiment_score", 0) for r in br) / len(br) if br else 0

        if avg_sentiment > 0.5:
            label = "very_positive"
        elif avg_sentiment > 0.1:
            label = "positive"
        elif avg_sentiment > -0.1:
            label = "neutral"
        elif avg_sentiment > -0.5:
            label = "negative"
        else:
            label = "very_negative"

        # Collect top pros/cons from products
        all_pros = []
        all_cons = []
        for p in bp:
            all_pros.extend(p.get("appreciation_themes", []))
            all_cons.extend(p.get("complaint_themes", []))

        from collections import Counter
        top_pros = [t for t, _ in Counter(all_pros).most_common(3)] if all_pros else ["N/A"]
        top_cons = [t for t, _ in Counter(all_cons).most_common(3)] if all_cons else ["N/A"]

        brand_summaries.append({
            "name": brand,
            "slug": brand.lower().replace(" ", "-"),
            "product_count": len(bp),
            "review_count": len(br),
            "avg_price": pricing_data.get("avg_price", 0),
            "avg_discount": pricing_data.get("avg_discount", 0),
            "avg_rating": round(sum(p.get("rating", 0) for p in bp) / len(bp), 1) if bp else 0,
            "sentiment_score": round(avg_sentiment, 2),
            "sentiment_label": label,
            "top_pros": top_pros,
            "top_cons": top_cons,
            "price_band": pricing_data.get("price_band", "midrange"),
            "aspect_scores": brand_aspects.get(brand, {}),
        })

    # Step 8: Anomaly detection
    print("\nStep 8: Detecting anomalies...")
    anomalies = detect_anomalies(products_list, reviews_list)

    # Step 9: Generate insights
    print("\nStep 9: Generating agent insights...")
    if not skip_llm:
        insights = generate_insights(brand_summaries, products_list)
    else:
        from backend.processing.insights_generator import _fallback_insights
        insights = _fallback_insights(brand_summaries)

    # Step 10: Value for money
    print("\nStep 10: Computing value-for-money...")
    max_price = max((b["avg_price"] for b in brand_summaries), default=1)
    value_for_money = [
        {
            "brand": b["name"],
            "price_band": b["price_band"],
            "avg_price": b["avg_price"],
            "sentiment_score": b["sentiment_score"],
            "value_score": round(
                b["sentiment_score"] * (1 - b["avg_price"] / max_price / 1.5) * 100, 1
            ),
        }
        for b in brand_summaries
    ]

    # Step 11: Filter options
    prices = [p["price"] for p in products_list]
    ratings = [p.get("rating", 0) for p in products_list]
    sentiments = [p.get("sentiment_score", 0) for p in products_list]
    filter_options = {
        "brands": sorted(brands),
        "price_range": {"min": min(prices) if prices else 0, "max": max(prices) if prices else 0},
        "rating_range": {"min": min(ratings) if ratings else 0, "max": max(ratings) if ratings else 5},
        "categories": sorted(set(p.get("category", "") for p in products_list if p.get("category"))),
        "sizes": sorted(set(p.get("size", "") for p in products_list if p.get("size"))),
        "sentiment_range": {"min": min(sentiments) if sentiments else -1, "max": max(sentiments) if sentiments else 1},
    }

    # Step 12: Aspect sentiments matrix
    aspect_sentiments = [
        {"brand": b["name"], **b["aspect_scores"]}
        for b in brand_summaries
    ]

    # Write all files
    print("\nWriting processed data...")
    files = {
        "products.json": products_list,
        "reviews_analyzed.json": reviews_list,
        "brands_summary.json": brand_summaries,
        "aspect_sentiments.json": aspect_sentiments,
        "anomalies.json": anomalies,
        "insights.json": insights,
        "value_for_money.json": value_for_money,
        "trust_signals.json": trust_signals,
        "filter_options.json": filter_options,
    }

    for filename, data in files.items():
        path = PROCESSED_DIR / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  Written {path}")

    print(f"\nPipeline complete! {len(brands)} brands, {len(products_list)} products, {len(reviews_list)} reviews.")
