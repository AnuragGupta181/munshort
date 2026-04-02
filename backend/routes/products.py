from fastapi import APIRouter, HTTPException, Query
from backend.config import load_json

router = APIRouter()


@router.get("/products")
def get_products(
    brand: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    min_rating: float | None = Query(None),
    min_sentiment: float | None = Query(None),
    category: str | None = Query(None),
    sort_by: str = Query("sentiment_score"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    products = load_json("products.json")

    if brand:
        products = [p for p in products if p["brand"] == brand]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]
    if min_rating is not None:
        products = [p for p in products if p["rating"] >= min_rating]
    if min_sentiment is not None:
        products = [p for p in products if p["sentiment_score"] >= min_sentiment]
    if category:
        products = [p for p in products if p.get("category") == category]

    reverse = order == "desc"
    if products and sort_by in products[0]:
        products.sort(key=lambda p: p.get(sort_by, 0), reverse=reverse)

    total = len(products)
    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "products": products[start:end],
    }


@router.get("/products/{asin}")
def get_product(asin: str):
    products = load_json("products.json")
    reviews = load_json("reviews_analyzed.json")

    product = next((p for p in products if p["asin"] == asin), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_reviews = [r for r in reviews if r["product_asin"] == asin]
    return {
        **product,
        "reviews": product_reviews,
    }
