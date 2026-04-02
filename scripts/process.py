"""Entry point for the processing pipeline.

Usage:
    uv run python scripts/process.py
    uv run python scripts/process.py --force
    uv run python scripts/process.py --skip-llm
"""

import click
from backend.processing.pipeline import run_pipeline


@click.command()
@click.option("--force", is_flag=True, help="Force reprocessing even if output exists")
@click.option("--skip-llm", is_flag=True, help="Skip Gemini API calls, use fallback heuristics")
def main(force: bool, skip_llm: bool):
    """Process raw scraped data into dashboard-ready JSON."""
    run_pipeline(force=force, skip_llm=skip_llm)


if __name__ == "__main__":
    main()
