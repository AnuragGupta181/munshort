"""Generate realistic sample data for the luggage brand dashboard.

Uses a fixed seed for reproducibility. No external API calls needed.
"""

import json
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = BASE_DIR / "data" / "sample"

BRANDS = {
    "Safari": {
        "slug": "safari",
        "tier": "budget",
        "price_range": (1200, 3500),
        "discount_range": (35, 55),
        "rating_mean": 3.9,
        "sentiment_mean": 0.35,
        "strengths": ["Affordable pricing", "Lightweight design", "Good color options"],
        "weaknesses": ["Zipper quality issues", "Wheels break easily", "Thin material"],
    },
    "Aristocrat": {
        "slug": "aristocrat",
        "tier": "value",
        "price_range": (1500, 4000),
        "discount_range": (40, 58),
        "rating_mean": 3.8,
        "sentiment_mean": 0.28,
        "strengths": ["Budget-friendly", "Decent storage space", "Lightweight"],
        "weaknesses": ["Handle durability", "Zipper breaks after few uses", "Material tears easily"],
    },
    "Skybags": {
        "slug": "skybags",
        "tier": "midrange",
        "price_range": (2500, 5500),
        "discount_range": (25, 42),
        "rating_mean": 4.1,
        "sentiment_mean": 0.52,
        "strengths": ["Trendy designs", "Smooth wheels", "Good build quality"],
        "weaknesses": ["Slightly overpriced", "Handle gets loose", "Limited warranty service"],
    },
    "VIP": {
        "slug": "vip",
        "tier": "midrange",
        "price_range": (2800, 6000),
        "discount_range": (28, 45),
        "rating_mean": 4.0,
        "sentiment_mean": 0.45,
        "strengths": ["Trusted brand", "Sturdy build", "Good wheel quality"],
        "weaknesses": ["Heavy weight", "Expensive for features", "Dull designs"],
    },
    "American Tourister": {
        "slug": "american-tourister",
        "tier": "premium",
        "price_range": (4000, 9500),
        "discount_range": (15, 35),
        "rating_mean": 4.3,
        "sentiment_mean": 0.68,
        "strengths": ["Excellent durability", "Premium material", "Smooth 360 wheels"],
        "weaknesses": ["High price point", "Heavy", "Limited color options at lower price"],
    },
    "Nasher Miles": {
        "slug": "nasher-miles",
        "tier": "premium",
        "price_range": (3500, 12000),
        "discount_range": (10, 25),
        "rating_mean": 4.4,
        "sentiment_mean": 0.72,
        "strengths": ["Premium look and feel", "Hard shell durability", "TSA-approved locks"],
        "weaknesses": ["Very expensive", "Scratches easily on hard shell", "Limited service centers"],
    },
}

CATEGORIES = ["Cabin", "Check-in", "Medium", "Small"]
SIZES = ["55cm / 20in", "65cm / 24in", "75cm / 28in", "50cm / 18in"]
MATERIALS = ["Polycarbonate", "Polypropylene", "Polyester", "ABS", "Nylon", "Hard Shell ABS+PC"]
COLORS = ["Blue", "Red", "Black", "Grey", "Teal", "Wine Red", "Navy", "Silver", "Crimson", "Charcoal"]

ASPECTS = ["wheels", "handle", "material", "zipper", "size_space", "durability"]

POSITIVE_REVIEW_TEMPLATES = [
    "Great {aspect}! Very happy with this purchase. The {brand} bag is exactly what I needed for my trip.",
    "Excellent quality {aspect}. Worth every rupee. Used it for 3 trips already and no issues at all.",
    "The {aspect} on this bag is top-notch. {brand} never disappoints. Highly recommended!",
    "Very satisfied with the {aspect}. Smooth and sturdy. Perfect for frequent travelers.",
    "Amazing {aspect} quality. I've used many brands but {brand} stands out. Good value for money.",
    "Bought this for my vacation and the {aspect} is fantastic. Looks premium and feels durable.",
    "Love the {aspect}. Very well built. The design is also very attractive. Five stars from me.",
    "Superb {aspect}. {brand} has outdone themselves with this product. Will buy again.",
    "The {aspect} is really good. No complaints so far after 2 months of use. Recommended.",
    "Happy customer! The {aspect} quality exceeded my expectations. Great bag overall.",
]

NEGATIVE_REVIEW_TEMPLATES = [
    "The {aspect} broke within a week of use. Very disappointed with {brand}. Not worth the price.",
    "Poor {aspect} quality. Expected better from {brand}. Will not buy again.",
    "Terrible {aspect}. Stopped working after first trip. Waste of money. Avoid this product.",
    "Very bad {aspect}. The quality does not match the price. {brand} needs to improve this.",
    "{aspect} is the weakest point. Everything else is ok but this ruins the entire experience.",
    "Disappointed with the {aspect}. It started showing problems after just 2 weeks of use.",
    "The {aspect} quality is subpar. My old ₹500 bag had better {aspect}. Don't recommend.",
    "Worst {aspect} ever. Returned the product. {brand} should focus on quality control.",
    "{aspect} failed during my trip. Very embarrassing at the airport. Will never buy {brand} again.",
    "For the price I paid, the {aspect} should be much better. Feels cheap and flimsy.",
]

NEUTRAL_REVIEW_TEMPLATES = [
    "The {aspect} is okay, nothing special. Decent for the price. {brand} is average in this regard.",
    "Average {aspect}. Not bad but not great either. Works for occasional travel.",
    "The {aspect} is decent. Could be better but it does the job. Acceptable quality for the price.",
    "Neither impressed nor disappointed with the {aspect}. It is what it is. Meets basic expectations.",
    "The {aspect} is satisfactory. Nothing to complain about but nothing to praise either.",
]

ASPECT_DISPLAY = {
    "wheels": "wheels",
    "handle": "handle",
    "material": "material quality",
    "zipper": "zipper",
    "size_space": "storage space",
    "durability": "durability",
}


def generate_asin():
    return "B0" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))


def generate_products():
    """Generate product data for all brands."""
    products = []
    for brand_name, info in BRANDS.items():
        for i in range(random.randint(10, 12)):
            category = random.choice(CATEGORIES)
            size = random.choice(SIZES)
            material = random.choice(MATERIALS)
            color = random.choice(COLORS)
            list_price = random.randint(info["price_range"][0], info["price_range"][1])
            list_price = round(list_price / 100) * 100  # round to nearest 100
            discount_pct = random.uniform(info["discount_range"][0], info["discount_range"][1])
            discount_pct = round(discount_pct, 1)
            price = round(list_price * (1 - discount_pct / 100))
            rating = round(
                max(1.0, min(5.0, random.gauss(info["rating_mean"], 0.3))), 1
            )
            review_count = random.randint(40, 850)

            # Generate aspect scores for this product
            aspect_scores = {}
            for aspect in ASPECTS:
                base = info["sentiment_mean"]
                noise = random.gauss(0, 0.2)
                # Weaken aspects that are brand weaknesses
                weakness_aspects = {
                    "Zipper quality issues": "zipper",
                    "Zipper breaks after few uses": "zipper",
                    "Wheels break easily": "wheels",
                    "Handle durability": "handle",
                    "Handle gets loose": "handle",
                    "Thin material": "material",
                    "Material tears easily": "material",
                    "Heavy weight": "durability",
                    "Heavy": "durability",
                    "Scratches easily on hard shell": "durability",
                }
                for weakness in info["weaknesses"]:
                    if weakness_aspects.get(weakness) == aspect:
                        noise -= 0.3
                # Strengthen aspects that are brand strengths
                strength_aspects = {
                    "Smooth wheels": "wheels",
                    "Smooth 360 wheels": "wheels",
                    "Good wheel quality": "wheels",
                    "Premium material": "material",
                    "Hard shell durability": "durability",
                    "Excellent durability": "durability",
                    "Sturdy build": "durability",
                    "Good build quality": "material",
                    "TSA-approved locks": "zipper",
                    "Good storage space": "size_space",
                    "Decent storage space": "size_space",
                }
                for strength in info["strengths"]:
                    if strength_aspects.get(strength) == aspect:
                        noise += 0.25
                aspect_scores[aspect] = round(max(-1.0, min(1.0, base + noise)), 2)

            sentiment_score = round(
                max(-1.0, min(1.0, random.gauss(info["sentiment_mean"], 0.15))), 2
            )

            product_title = f"{brand_name} {material} {category} Luggage Trolley Bag {size.split('/')[0].strip()} - {color}"

            # Generate review synthesis
            pros = random.sample(info["strengths"], min(2, len(info["strengths"])))
            cons = random.sample(info["weaknesses"], min(2, len(info["weaknesses"])))
            synthesis = (
                f"Customers generally {'appreciate' if sentiment_score > 0.3 else 'have mixed feelings about'} this {brand_name} product. "
                f"Key positives include {pros[0].lower()} and {pros[1].lower() if len(pros) > 1 else 'overall value'}. "
                f"Common concerns revolve around {cons[0].lower()}"
                + (f" and {cons[1].lower()}" if len(cons) > 1 else "")
                + "."
            )

            products.append(
                {
                    "asin": generate_asin(),
                    "title": product_title,
                    "brand": brand_name,
                    "price": price,
                    "list_price": list_price,
                    "discount_pct": discount_pct,
                    "rating": rating,
                    "review_count": review_count,
                    "sentiment_score": sentiment_score,
                    "review_synthesis": synthesis,
                    "complaint_themes": cons,
                    "appreciation_themes": pros,
                    "trust_score": round(random.uniform(55, 95), 1),
                    "aspects": aspect_scores,
                    "category": category,
                    "size": size,
                }
            )
    return products


def generate_reviews(products: list[dict]):
    """Generate review data for all products."""
    reviews = []
    for product in products:
        brand_name = product["brand"]
        info = BRANDS[brand_name]
        num_reviews = random.randint(5, 12)

        for _ in range(num_reviews):
            rating = max(
                1, min(5, int(random.gauss(info["rating_mean"], 1.0)))
            )
            aspect = random.choice(ASPECTS)
            aspect_display = ASPECT_DISPLAY[aspect]

            if rating >= 4:
                template = random.choice(POSITIVE_REVIEW_TEMPLATES)
                sentiment_score = round(random.uniform(0.3, 1.0), 2)
                sentiment_label = (
                    "very_positive" if sentiment_score > 0.7 else "positive"
                )
                title = random.choice(
                    [
                        "Great product!",
                        "Value for money",
                        "Highly recommended",
                        "Excellent quality",
                        "Love it!",
                        "Perfect for travel",
                        "Good buy",
                        "Very satisfied",
                    ]
                )
            elif rating <= 2:
                template = random.choice(NEGATIVE_REVIEW_TEMPLATES)
                sentiment_score = round(random.uniform(-1.0, -0.2), 2)
                sentiment_label = (
                    "very_negative" if sentiment_score < -0.6 else "negative"
                )
                title = random.choice(
                    [
                        "Disappointed",
                        "Not worth it",
                        "Poor quality",
                        "Waste of money",
                        "Terrible product",
                        "Broke quickly",
                        "Don't buy",
                        "Very bad",
                    ]
                )
            else:
                template = random.choice(NEUTRAL_REVIEW_TEMPLATES)
                sentiment_score = round(random.uniform(-0.2, 0.3), 2)
                sentiment_label = "neutral"
                title = random.choice(
                    [
                        "Okay product",
                        "Average quality",
                        "Decent",
                        "Not bad",
                        "Meets expectations",
                        "It's alright",
                    ]
                )

            body = template.format(aspect=aspect_display, brand=brand_name)
            date = datetime.now() - timedelta(days=random.randint(1, 365))
            verified = random.random() > 0.15
            helpful_votes = (
                random.randint(0, 30) if rating in (1, 2, 5) else random.randint(0, 10)
            )
            aspects_mentioned = [aspect]
            if random.random() > 0.5:
                extra = random.choice([a for a in ASPECTS if a != aspect])
                aspects_mentioned.append(extra)

            reviews.append(
                {
                    "id": str(uuid.uuid4())[:12],
                    "product_asin": product["asin"],
                    "brand": brand_name,
                    "rating": rating,
                    "title": title,
                    "body": body,
                    "date": date.strftime("%Y-%m-%d"),
                    "verified": verified,
                    "helpful_votes": helpful_votes,
                    "sentiment_score": sentiment_score,
                    "sentiment_label": sentiment_label,
                    "aspects_mentioned": aspects_mentioned,
                }
            )
    return reviews


def generate_brand_summaries(products: list[dict], reviews: list[dict]):
    """Compute brand-level aggregations."""
    summaries = []
    for brand_name, info in BRANDS.items():
        brand_products = [p for p in products if p["brand"] == brand_name]
        brand_reviews = [r for r in reviews if r["brand"] == brand_name]

        avg_price = sum(p["price"] for p in brand_products) / len(brand_products)
        avg_list = sum(p["list_price"] for p in brand_products) / len(brand_products)
        avg_discount = round(
            (1 - avg_price / avg_list) * 100 if avg_list > 0 else 0, 1
        )
        avg_rating = sum(p["rating"] for p in brand_products) / len(brand_products)
        sentiment = sum(r["sentiment_score"] for r in brand_reviews) / len(
            brand_reviews
        )

        # Aspect aggregation
        aspect_scores = {}
        for aspect in ASPECTS:
            scores = [p["aspects"].get(aspect, 0) for p in brand_products]
            aspect_scores[aspect] = round(sum(scores) / len(scores), 2)

        if sentiment > 0.5:
            label = "very_positive" if sentiment > 0.7 else "positive"
        elif sentiment > 0.1:
            label = "positive" if sentiment > 0.3 else "neutral"
        elif sentiment > -0.3:
            label = "neutral" if sentiment > -0.1 else "negative"
        else:
            label = "very_negative" if sentiment < -0.6 else "negative"

        tier_map = {"budget": "budget", "value": "value", "midrange": "midrange", "premium": "premium"}

        summaries.append(
            {
                "name": brand_name,
                "slug": info["slug"],
                "product_count": len(brand_products),
                "review_count": len(brand_reviews),
                "avg_price": round(avg_price, 0),
                "avg_discount": avg_discount,
                "avg_rating": round(avg_rating, 1),
                "sentiment_score": round(sentiment, 2),
                "sentiment_label": label,
                "top_pros": info["strengths"],
                "top_cons": info["weaknesses"],
                "price_band": tier_map[info["tier"]],
                "aspect_scores": aspect_scores,
            }
        )
    return summaries


def generate_aspect_sentiments(brand_summaries: list[dict]):
    """Extract the aspect × brand matrix."""
    return [
        {
            "brand": s["name"],
            **s["aspect_scores"],
        }
        for s in brand_summaries
    ]


def generate_anomalies(products: list[dict]):
    """Generate realistic anomaly detections."""
    anomalies = []
    for p in products:
        # High rating but negative sentiment
        if p["rating"] >= 4.0 and p["sentiment_score"] < 0.1:
            anomalies.append(
                {
                    "type": "sentiment_rating_divergence",
                    "severity": "warning",
                    "brand": p["brand"],
                    "product_title": p["title"],
                    "description": f"Product has {p['rating']} stars but sentiment score is only {p['sentiment_score']:.2f}. Reviews suggest underlying quality concerns despite high rating.",
                }
            )
        # High discount suggests inflated MRP
        if p["discount_pct"] > 50:
            anomalies.append(
                {
                    "type": "suspicious_pricing",
                    "severity": "info",
                    "brand": p["brand"],
                    "product_title": p["title"],
                    "description": f"Discount of {p['discount_pct']}% (₹{p['list_price']} → ₹{p['price']}) suggests potentially inflated list price.",
                }
            )
        # Durability complaints despite good rating
        if (
            p["rating"] >= 4.0
            and p["aspects"].get("durability", 0) < -0.1
        ):
            anomalies.append(
                {
                    "type": "durability_concern",
                    "severity": "critical",
                    "brand": p["brand"],
                    "product_title": p["title"],
                    "description": f"Despite {p['rating']} star rating, durability aspect sentiment is negative ({p['aspects']['durability']:.2f}). Customers report breakage issues.",
                }
            )
    return anomalies[:15]  # Cap at 15 most interesting


def generate_insights(brand_summaries: list[dict], products: list[dict]):
    """Generate 5 non-obvious agent insights."""
    # Sort brands by sentiment
    by_sentiment = sorted(brand_summaries, key=lambda x: x["sentiment_score"], reverse=True)
    best = by_sentiment[0]
    worst = by_sentiment[-1]

    # Find the best value brand (highest sentiment in budget/value tier)
    budget_brands = [b for b in brand_summaries if b["price_band"] in ("budget", "value")]
    best_value = max(budget_brands, key=lambda x: x["sentiment_score"]) if budget_brands else best

    # Find most discount-dependent
    most_discounted = max(brand_summaries, key=lambda x: x["avg_discount"])

    # Find aspect leaders
    aspect_leaders = {}
    for aspect in ASPECTS:
        leader = max(brand_summaries, key=lambda x: x["aspect_scores"].get(aspect, 0))
        aspect_leaders[aspect] = leader["name"]

    return [
        {
            "title": f"{best['name']} leads in customer sentiment despite {'not being the cheapest' if best['price_band'] == 'premium' else 'competitive pricing'}",
            "description": f"{best['name']} achieves the highest overall sentiment score ({best['sentiment_score']:.2f}) across all brands. This suggests strong product-market fit where customers feel they receive value proportional to or exceeding the price paid. Their strength in {list(best['aspect_scores'].keys())[0]} and {list(best['aspect_scores'].keys())[1]} aspects particularly stands out.",
            "supporting_data": [
                f"Sentiment score: {best['sentiment_score']:.2f} vs category average {sum(b['sentiment_score'] for b in brand_summaries) / len(brand_summaries):.2f}",
                f"Average rating: {best['avg_rating']}",
                f"Price band: {best['price_band']}",
            ],
            "affected_brands": [best["name"]],
            "insight_type": "competitive_advantage",
        },
        {
            "title": f"{most_discounted['name']}'s heavy discounting ({most_discounted['avg_discount']:.0f}%) isn't translating to better sentiment",
            "description": f"Despite offering the highest average discount at {most_discounted['avg_discount']:.0f}%, {most_discounted['name']} ranks lower in customer sentiment ({most_discounted['sentiment_score']:.2f}). This indicates that price reduction alone doesn't compensate for product quality gaps. The brand may be caught in a discount dependency cycle where deep discounts set low quality expectations.",
            "supporting_data": [
                f"Average discount: {most_discounted['avg_discount']:.0f}%",
                f"Sentiment score: {most_discounted['sentiment_score']:.2f}",
                f"Average price after discount: ₹{most_discounted['avg_price']:.0f}",
            ],
            "affected_brands": [most_discounted["name"]],
            "insight_type": "pricing_strategy",
        },
        {
            "title": f"Zipper quality is the category's Achilles heel — {aspect_leaders.get('zipper', 'N/A')} leads but gap is narrow",
            "description": f"Across all brands, zipper quality receives some of the most polarized feedback. Even top-performing brands struggle with zipper durability perception. This represents an opportunity for any brand to differentiate by investing in premium zipper components (YKK or equivalent) and communicating this in product listings.",
            "supporting_data": [
                f"Best zipper sentiment: {max(b['aspect_scores'].get('zipper', 0) for b in brand_summaries):.2f}",
                f"Worst zipper sentiment: {min(b['aspect_scores'].get('zipper', 0) for b in brand_summaries):.2f}",
                f"Category average: {sum(b['aspect_scores'].get('zipper', 0) for b in brand_summaries) / len(brand_summaries):.2f}",
            ],
            "affected_brands": list(set(aspect_leaders.values())),
            "insight_type": "product_gap",
        },
        {
            "title": f"{best_value['name']} offers the best value proposition in the budget segment",
            "description": f"Among budget and value-tier brands, {best_value['name']} achieves the highest sentiment ({best_value['sentiment_score']:.2f}) while maintaining competitive pricing (avg ₹{best_value['avg_price']:.0f}). Price-conscious buyers rate {best_value['name']} higher than peers, suggesting the brand successfully delivers perceived quality above its price tier.",
            "supporting_data": [
                f"Sentiment: {best_value['sentiment_score']:.2f} (best in budget/value tier)",
                f"Average price: ₹{best_value['avg_price']:.0f}",
                f"Price band: {best_value['price_band']}",
            ],
            "affected_brands": [best_value["name"]],
            "insight_type": "value_analysis",
        },
        {
            "title": f"Wheel quality strongly correlates with overall satisfaction — {aspect_leaders.get('wheels', 'N/A')} dominates",
            "description": f"Analysis shows that wheel quality sentiment has the strongest correlation with overall product sentiment. Brands that score high on wheels consistently score higher overall. {aspect_leaders.get('wheels', 'The leader')} leads the category in wheel quality perception, which likely contributes to their strong overall sentiment. Brands looking to improve customer satisfaction should prioritize wheel mechanism upgrades.",
            "supporting_data": [
                f"Wheel quality leader: {aspect_leaders.get('wheels', 'N/A')}",
                f"Correlation with overall sentiment: high",
                f"Most mentioned aspect in positive reviews: wheels and durability",
            ],
            "affected_brands": [aspect_leaders.get("wheels", ""), aspect_leaders.get("durability", "")],
            "insight_type": "customer_driver",
        },
    ]


def generate_value_for_money(brand_summaries: list[dict]):
    """Compute value-for-money scores."""
    max_price = max(b["avg_price"] for b in brand_summaries)
    return [
        {
            "brand": b["name"],
            "price_band": b["price_band"],
            "avg_price": b["avg_price"],
            "sentiment_score": b["sentiment_score"],
            "value_score": round(
                b["sentiment_score"] * (1 - b["avg_price"] / max_price / 1.5) * 100,
                1,
            ),
        }
        for b in brand_summaries
    ]


def generate_trust_signals(products: list[dict], reviews: list[dict]):
    """Generate trust signal data per product."""
    signals = []
    for p in products:
        prod_reviews = [r for r in reviews if r["product_asin"] == p["asin"]]
        if not prod_reviews:
            continue
        verified_ratio = (
            sum(1 for r in prod_reviews if r["verified"]) / len(prod_reviews)
        )
        five_star_ratio = (
            sum(1 for r in prod_reviews if r["rating"] == 5) / len(prod_reviews)
        )
        avg_length = sum(len(r["body"]) for r in prod_reviews) / len(prod_reviews)
        trust_score = p["trust_score"]

        flags = []
        if five_star_ratio > 0.8:
            flags.append("Unusually high 5-star ratio")
        if verified_ratio < 0.6:
            flags.append("Low verified purchase ratio")
        if avg_length < 50:
            flags.append("Very short average review length")

        signals.append(
            {
                "asin": p["asin"],
                "brand": p["brand"],
                "product_title": p["title"],
                "trust_score": trust_score,
                "verified_ratio": round(verified_ratio * 100, 1),
                "five_star_ratio": round(five_star_ratio * 100, 1),
                "avg_review_length": round(avg_length),
                "total_reviews": len(prod_reviews),
                "flags": flags,
            }
        )
    return signals


def generate_filter_options(products: list[dict]):
    """Compute available filter values."""
    prices = [p["price"] for p in products]
    ratings = [p["rating"] for p in products]
    sentiments = [p["sentiment_score"] for p in products]
    return {
        "brands": sorted(set(p["brand"] for p in products)),
        "price_range": {"min": min(prices), "max": max(prices)},
        "rating_range": {"min": min(ratings), "max": max(ratings)},
        "categories": sorted(set(p["category"] for p in products)),
        "sizes": sorted(set(p["size"] for p in products)),
        "sentiment_range": {"min": min(sentiments), "max": max(sentiments)},
    }


def main():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating products...")
    products = generate_products()

    print("Generating reviews...")
    reviews = generate_reviews(products)

    print("Computing brand summaries...")
    brand_summaries = generate_brand_summaries(products, reviews)

    print("Generating aspect sentiments...")
    aspects = generate_aspect_sentiments(brand_summaries)

    print("Generating anomalies...")
    anomalies = generate_anomalies(products)

    print("Generating insights...")
    insights = generate_insights(brand_summaries, products)

    print("Computing value-for-money...")
    vfm = generate_value_for_money(brand_summaries)

    print("Generating trust signals...")
    trust = generate_trust_signals(products, reviews)

    print("Computing filter options...")
    filters = generate_filter_options(products)

    # Write all files
    files = {
        "products.json": products,
        "reviews_analyzed.json": reviews,
        "brands_summary.json": brand_summaries,
        "aspect_sentiments.json": aspects,
        "anomalies.json": anomalies,
        "insights.json": insights,
        "value_for_money.json": vfm,
        "trust_signals.json": trust,
        "filter_options.json": filters,
    }

    for filename, data in files.items():
        path = SAMPLE_DIR / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Written {path} ({len(json.dumps(data))} bytes)")

    print(f"\nDone! Generated data for {len(BRANDS)} brands, {len(products)} products, {len(reviews)} reviews.")
    print(f"Sample data directory: {SAMPLE_DIR}")


if __name__ == "__main__":
    main()
