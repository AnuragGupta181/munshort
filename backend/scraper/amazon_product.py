"""Scrape Amazon India product detail pages."""

import re
from playwright.async_api import Page
from backend.scraper.rate_limiter import RateLimiter


async def scrape_product_detail(
    page: Page,
    asin: str,
    rate_limiter: RateLimiter | None = None,
) -> dict:
    """Scrape detailed product information from a product page."""
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    url = f"https://www.amazon.in/dp/{asin}"
    print(f"    Fetching product detail: {asin}")

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(1500)

    detail = {"asin": asin}

    # Title
    title_el = await page.query_selector("#productTitle")
    if title_el:
        detail["title"] = (await title_el.inner_text()).strip()

    # Brand
    brand_el = await page.query_selector("#bylineInfo")
    if brand_el:
        brand_text = (await brand_el.inner_text()).strip()
        detail["brand_line"] = brand_text.replace("Visit the ", "").replace("Brand: ", "").replace(" Store", "")

    # Price
    price_el = await page.query_selector("span.a-price-whole")
    if price_el:
        price_text = await price_el.inner_text()
        detail["price"] = int(re.sub(r"[^\d]", "", price_text) or 0)

    # List price
    lp_el = await page.query_selector("span.a-price.a-text-price span.a-offscreen")
    if lp_el:
        lp_text = await lp_el.inner_text()
        detail["list_price"] = int(re.sub(r"[^\d]", "", lp_text) or 0)

    # Rating
    rating_el = await page.query_selector("#acrPopover span.a-icon-alt")
    if rating_el:
        rating_text = await rating_el.inner_text()
        match = re.search(r"([\d.]+)", rating_text)
        if match:
            detail["rating"] = float(match.group(1))

    # Review count
    review_el = await page.query_selector("#acrCustomerReviewText")
    if review_el:
        rc_text = await review_el.inner_text()
        rc_clean = re.sub(r"[^\d]", "", rc_text)
        detail["review_count"] = int(rc_clean) if rc_clean else 0

    # Features / bullet points
    features = []
    feature_els = await page.query_selector_all("#feature-bullets ul li span.a-list-item")
    for el in feature_els:
        text = (await el.inner_text()).strip()
        if text and not text.startswith("›"):
            features.append(text)
    detail["features"] = features[:8]

    return detail
