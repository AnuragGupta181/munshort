"""Scrape Amazon India search results for luggage products."""

import re
from playwright.async_api import Page
from backend.scraper.rate_limiter import RateLimiter


async def scrape_search_results(
    page: Page,
    brand: str,
    max_products: int = 12,
    rate_limiter: RateLimiter | None = None,
) -> list[dict]:
    """Search Amazon India for a brand's luggage products and extract basic data."""
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    query = f"{brand} luggage trolley bag"
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"

    print(f"  Searching: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)

    products = []
    page_num = 1

    while len(products) < max_products and page_num <= 3:
        # Extract product cards from search results
        cards = await page.query_selector_all('[data-component-type="s-search-result"]')

        for card in cards:
            if len(products) >= max_products:
                break
            try:
                product = await _extract_search_card(card, brand)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"    Warning: Failed to extract card: {e}")
                continue

        # Try next page
        next_btn = await page.query_selector('a.s-pagination-next:not(.s-pagination-disabled)')
        if not next_btn or len(products) >= max_products:
            break

        page_num += 1
        await rate_limiter.wait()
        await next_btn.click()
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)

    print(f"  Found {len(products)} products for {brand}")
    return products


async def _extract_search_card(card, brand: str) -> dict | None:
    """Extract product data from a single search result card."""
    asin = await card.get_attribute("data-asin")
    if not asin:
        return None

    # Title
    title_el = await card.query_selector("h2 a span")
    title = await title_el.inner_text() if title_el else ""
    if not title:
        return None

    # Price
    price_whole = await card.query_selector("span.a-price-whole")
    price = 0
    if price_whole:
        price_text = await price_whole.inner_text()
        price = int(re.sub(r"[^\d]", "", price_text) or 0)

    # Original price (list price)
    list_price_el = await card.query_selector("span.a-price.a-text-price span.a-offscreen")
    list_price = price
    if list_price_el:
        lp_text = await list_price_el.inner_text()
        list_price = int(re.sub(r"[^\d]", "", lp_text) or price)

    # Rating
    rating_el = await card.query_selector("span.a-icon-alt")
    rating = 0.0
    if rating_el:
        rating_text = await rating_el.inner_text()
        match = re.search(r"([\d.]+)", rating_text)
        if match:
            rating = float(match.group(1))

    # Review count
    review_el = await card.query_selector('span[aria-label*="ratings"] span.a-size-base, a[href*="#customerReviews"] span')
    review_count = 0
    if review_el:
        rc_text = await review_el.inner_text()
        rc_clean = re.sub(r"[^\d]", "", rc_text)
        review_count = int(rc_clean) if rc_clean else 0

    if price == 0:
        return None

    discount_pct = round((1 - price / list_price) * 100, 1) if list_price > price else 0

    return {
        "asin": asin,
        "title": title.strip(),
        "brand": brand,
        "price": price,
        "list_price": list_price,
        "discount_pct": discount_pct,
        "rating": rating,
        "review_count": review_count,
    }
