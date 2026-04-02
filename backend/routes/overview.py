from fastapi import APIRouter
from backend.config import load_json

router = APIRouter()


@router.get("/overview")
def get_overview():
    brands = load_json("brands_summary.json")
    products = load_json("products.json")
    reviews = load_json("reviews_analyzed.json")

    if not brands:
        return {"total_brands": 0, "total_products": 0, "total_reviews": 0}

    prices = [p["price"] for p in products]
    return {
        "total_brands": len(brands),
        "total_products": len(products),
        "total_reviews": len(reviews),
        "avg_sentiment": round(
            sum(b["sentiment_score"] for b in brands) / len(brands), 2
        ),
        "avg_price": round(sum(prices) / len(prices), 0) if prices else 0,
        "avg_discount": round(
            sum(b["avg_discount"] for b in brands) / len(brands), 1
        ),
        "price_range": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
        },
        "brand_summaries": brands,
    }
