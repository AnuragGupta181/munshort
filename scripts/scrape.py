"""Entry point for the scraper CLI.

Usage:
    uv run python scripts/scrape.py all --max-products 12
    uv run python scripts/scrape.py brand Safari --max-products 5
"""

from backend.scraper.cli import cli

if __name__ == "__main__":
    cli()
