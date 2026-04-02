from fastapi import APIRouter, Query
from backend.config import load_json

router = APIRouter()


@router.get("/reviews")
def get_reviews(
    brand: str | None = Query(None),
    product_asin: str | None = Query(None),
    min_rating: int | None = Query(None),
    sentiment: str | None = Query(None),
    verified_only: bool = Query(False),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    reviews = load_json("reviews_analyzed.json")

    if brand:
        reviews = [r for r in reviews if r["brand"] == brand]
    if product_asin:
        reviews = [r for r in reviews if r["product_asin"] == product_asin]
    if min_rating is not None:
        reviews = [r for r in reviews if r["rating"] >= min_rating]
    if sentiment:
        reviews = [r for r in reviews if r["sentiment_label"] == sentiment]
    if verified_only:
        reviews = [r for r in reviews if r["verified"]]

    total = len(reviews)
    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "reviews": reviews[start:end],
    }
