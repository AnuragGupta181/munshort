from pydantic import BaseModel
from backend.models.enums import PriceBand, SentimentLevel


class BrandSummary(BaseModel):
    name: str
    slug: str
    product_count: int
    review_count: int
    avg_price: float
    avg_discount: float
    avg_rating: float
    sentiment_score: float
    sentiment_label: SentimentLevel
    top_pros: list[str]
    top_cons: list[str]
    price_band: PriceBand
    aspect_scores: dict[str, float]


class OverviewResponse(BaseModel):
    total_brands: int
    total_products: int
    total_reviews: int
    avg_sentiment: float
    avg_price: float
    avg_discount: float
    price_range: dict[str, float]
    brand_summaries: list[BrandSummary]


class ProductDetail(BaseModel):
    asin: str
    title: str
    brand: str
    price: float
    list_price: float
    discount_pct: float
    rating: float
    review_count: int
    sentiment_score: float
    review_synthesis: str
    complaint_themes: list[str]
    appreciation_themes: list[str]
    trust_score: float
    aspects: dict[str, float]
    category: str = ""
    size: str = ""


class ReviewDetail(BaseModel):
    id: str
    product_asin: str
    brand: str
    rating: int
    title: str
    body: str
    date: str
    verified: bool
    helpful_votes: int
    sentiment_score: float
    sentiment_label: SentimentLevel
    aspects_mentioned: list[str]


class InsightItem(BaseModel):
    title: str
    description: str
    supporting_data: list[str]
    affected_brands: list[str]
    insight_type: str


class AnomalyItem(BaseModel):
    type: str
    severity: str
    brand: str
    product_title: str
    description: str


class AspectData(BaseModel):
    brand: str
    wheels: float
    handle: float
    material: float
    zipper: float
    size_space: float
    durability: float


class ValueForMoney(BaseModel):
    brand: str
    price_band: PriceBand
    avg_price: float
    sentiment_score: float
    value_score: float


class FilterOptions(BaseModel):
    brands: list[str]
    price_range: dict[str, float]
    rating_range: dict[str, float]
    categories: list[str]
    sizes: list[str]
    sentiment_range: dict[str, float]
