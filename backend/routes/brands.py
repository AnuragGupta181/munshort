from fastapi import APIRouter, HTTPException, Query
from backend.config import load_json

router = APIRouter()


@router.get("/brands")
def get_brands(
    sort_by: str = Query("sentiment_score", description="Field to sort by"),
    order: str = Query("desc", description="asc or desc"),
):
    brands = load_json("brands_summary.json")
    reverse = order == "desc"
    if brands and sort_by in brands[0]:
        brands.sort(key=lambda b: b.get(sort_by, 0), reverse=reverse)
    return brands


@router.get("/brands/{slug}")
def get_brand(slug: str):
    brands = load_json("brands_summary.json")
    products = load_json("products.json")
    reviews = load_json("reviews_analyzed.json")

    brand = next((b for b in brands if b["slug"] == slug), None)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_products = [p for p in products if p["brand"] == brand["name"]]
    brand_reviews = [r for r in reviews if r["brand"] == brand["name"]]

    return {
        **brand,
        "products": brand_products,
        "reviews": brand_reviews,
    }
