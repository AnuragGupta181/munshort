"""CLI for the Amazon India luggage scraper."""

import asyncio
import json
from pathlib import Path

import click

from backend.scraper.browser import create_browser
from backend.scraper.amazon_search import scrape_search_results
from backend.scraper.amazon_reviews import scrape_reviews
from backend.scraper.rate_limiter import RateLimiter


BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

DEFAULT_BRANDS = ["Safari", "Skybags", "American Tourister", "VIP", "Aristocrat", "Nasher Miles"]


@click.group()
def cli():
    """Amazon India Luggage Scraper."""
    pass


@cli.command()
@click.option("--max-products", default=12, help="Max products per brand")
@click.option("--max-reviews", default=10, help="Max reviews per product")
@click.option("--headless/--no-headless", default=True, help="Run browser headless")
def all(max_products: int, max_reviews: int, headless: bool):
    """Scrape all default brands."""
    asyncio.run(_scrape_brands(DEFAULT_BRANDS, max_products, max_reviews, headless))


@cli.command()
@click.argument("name")
@click.option("--max-products", default=12, help="Max products per brand")
@click.option("--max-reviews", default=10, help="Max reviews per product")
@click.option("--headless/--no-headless", default=True, help="Run browser headless")
def brand(name: str, max_products: int, max_reviews: int, headless: bool):
    """Scrape a single brand by name."""
    asyncio.run(_scrape_brands([name], max_products, max_reviews, headless))


async def _scrape_brands(
    brands: list[str],
    max_products: int,
    max_reviews: int,
    headless: bool,
):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rate_limiter = RateLimiter()

    async with create_browser(headless=headless) as browser:
        for brand_name in brands:
            click.echo(f"\n{'='*60}")
            click.echo(f"Scraping: {brand_name}")
            click.echo(f"{'='*60}")

            try:
                # Search for products
                async with browser.get_page() as page:
                    products = await scrape_search_results(
                        page, brand_name, max_products, rate_limiter
                    )

                # Save products
                products_file = RAW_DIR / f"{brand_name.lower().replace(' ', '_')}_products.json"
                with open(products_file, "w") as f:
                    json.dump(products, f, indent=2)
                click.echo(f"  Saved {len(products)} products to {products_file}")

                # Scrape reviews for each product
                all_reviews = []
                for product in products:
                    await rate_limiter.wait()
                    async with browser.get_page() as page:
                        product_reviews = await scrape_reviews(
                            page,
                            product["asin"],
                            brand_name,
                            max_reviews,
                            rate_limiter,
                        )
                        all_reviews.extend(product_reviews)

                # Save reviews
                reviews_file = RAW_DIR / f"{brand_name.lower().replace(' ', '_')}_reviews.json"
                with open(reviews_file, "w") as f:
                    json.dump(all_reviews, f, indent=2)
                click.echo(f"  Saved {len(all_reviews)} reviews to {reviews_file}")

                rate_limiter.reset_backoff()

            except Exception as e:
                click.echo(f"  ERROR scraping {brand_name}: {e}")
                rate_limiter.increase_backoff()
                continue

    click.echo(f"\nDone! Raw data saved to {RAW_DIR}")


if __name__ == "__main__":
    cli()
