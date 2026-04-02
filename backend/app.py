from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import overview, brands, products, reviews, insights, filters

app = FastAPI(title="Luggage Brand Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router, prefix="/api")
app.include_router(brands.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(filters.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
