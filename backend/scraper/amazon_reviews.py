"""Scrape Amazon India product reviews."""

import re
from playwright.async_api import Page
from backend.scraper.rate_limiter import RateLimiter


async def scrape_reviews(
    page: Page,
    asin: str,
    brand: str,
    max_reviews: int = 10,
    rate_limiter: RateLimiter | None = None,
) -> list[dict]:
    """Scrape reviews for a product from Amazon India."""
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    url = f"https://www.amazon.in/product-reviews/{asin}/?sortBy=recent"
    print(f"    Fetching reviews for: {asin}")

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)

    reviews = []
    page_num = 1

    while len(reviews) < max_reviews and page_num <= 3:
        review_els = await page.query_selector_all('[data-hook="review"]')

        for el in review_els:
            if len(reviews) >= max_reviews:
                break
            try:
                review = await _extract_review(el, asin, brand)
                if review:
                    reviews.append(review)
            except Exception as e:
                print(f"      Warning: Failed to extract review: {e}")
                continue

        # Next page
        next_btn = await page.query_selector("li.a-last a")
        if not next_btn or len(reviews) >= max_reviews:
            break

        page_num += 1
        await rate_limiter.wait()
        await next_btn.click()
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)

    print(f"    Collected {len(reviews)} reviews for {asin}")
    return reviews


async def _extract_review(el, asin: str, brand: str) -> dict | None:
    """Extract a single review."""
    review_id_attr = await el.get_attribute("id")
    review_id = review_id_attr or ""

    # Rating
    rating_el = await el.query_selector('[data-hook="review-star-rating"] span.a-icon-alt, [data-hook="cmps-review-star-rating"] span.a-icon-alt')
    rating = 0
    if rating_el:
        rating_text = await rating_el.inner_text()
        match = re.search(r"([\d.]+)", rating_text)
        if match:
            rating = int(float(match.group(1)))

    # Title
    title_el = await el.query_selector('[data-hook="review-title"] span:not(.a-icon-alt), [data-hook="review-title"] a span:not(.a-icon-alt)')
    title = ""
    if title_el:
        title = (await title_el.inner_text()).strip()

    # Body
    body_el = await el.query_selector('[data-hook="review-body"] span')
    body = ""
    if body_el:
        body = (await body_el.inner_text()).strip()

    # Date
    date_el = await el.query_selector('[data-hook="review-date"]')
    date = ""
    if date_el:
        date = (await date_el.inner_text()).strip()

    # Verified
    verified_el = await el.query_selector('[data-hook="avp-badge"]')
    verified = verified_el is not None

    # Helpful votes
    helpful_el = await el.query_selector('[data-hook="helpful-vote-statement"]')
    helpful_votes = 0
    if helpful_el:
        h_text = await helpful_el.inner_text()
        h_match = re.search(r"(\d+)", h_text)
        if h_match:
            helpful_votes = int(h_match.group(1))

    if not body:
        return None

    return {
        "id": review_id,
        "product_asin": asin,
        "brand": brand,
        "rating": rating,
        "title": title,
        "body": body,
        "date": date,
        "verified": verified,
        "helpful_votes": helpful_votes,
    }
