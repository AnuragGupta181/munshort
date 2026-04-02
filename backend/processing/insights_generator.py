"""Generate agent insights using Gemini."""

import json
import os

from google import genai


def generate_insights(brand_summaries: list[dict], products: list[dict]) -> list[dict]:
    """Generate 5 non-obvious insights from the aggregated data."""
    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return _fallback_insights(brand_summaries)

        client = genai.Client(api_key=api_key)

        data_summary = json.dumps(brand_summaries, indent=2)

        prompt = f"""You are a competitive intelligence analyst for the Indian luggage market.
Given the following brand-level data from Amazon India, generate exactly 5 non-obvious, actionable insights.

Each insight should:
- Go beyond surface-level observations (don't just restate the numbers)
- Explain WHY a pattern exists or what it MEANS for a decision-maker
- Be supported by specific data points
- Identify one or more affected brands

Brand data:
{data_summary}

Return ONLY valid JSON in this format:
[
  {{
    "title": "Short, specific headline",
    "description": "2-3 sentences explaining the insight and its implications",
    "supporting_data": ["data point 1", "data point 2"],
    "affected_brands": ["Brand1", "Brand2"],
    "insight_type": "competitive_advantage|pricing_strategy|product_gap|value_analysis|customer_driver"
  }}
]"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        insights = json.loads(text)
        return insights[:5]

    except Exception as e:
        print(f"  Warning: Gemini insights generation failed: {e}")
        return _fallback_insights(brand_summaries)


def _fallback_insights(brand_summaries: list[dict]) -> list[dict]:
    """Generate basic insights without LLM."""
    if not brand_summaries:
        return []

    by_sentiment = sorted(brand_summaries, key=lambda x: x.get("sentiment_score", 0), reverse=True)
    best = by_sentiment[0]
    worst = by_sentiment[-1]
    most_discounted = max(brand_summaries, key=lambda x: x.get("avg_discount", 0))

    insights = [
        {
            "title": f"{best['name']} leads in customer sentiment",
            "description": f"{best['name']} achieves the highest sentiment score ({best.get('sentiment_score', 0):.2f}), suggesting strong product-market fit.",
            "supporting_data": [
                f"Sentiment: {best.get('sentiment_score', 0):.2f}",
                f"Rating: {best.get('avg_rating', 0):.1f}",
                f"Price band: {best.get('price_band', 'unknown')}",
            ],
            "affected_brands": [best["name"]],
            "insight_type": "competitive_advantage",
        },
        {
            "title": f"{most_discounted['name']}'s discounting strategy may not be working",
            "description": f"Despite the highest discount at {most_discounted.get('avg_discount', 0):.0f}%, {most_discounted['name']} doesn't lead in sentiment. Heavy discounting may signal quality concerns.",
            "supporting_data": [
                f"Discount: {most_discounted.get('avg_discount', 0):.0f}%",
                f"Sentiment: {most_discounted.get('sentiment_score', 0):.2f}",
            ],
            "affected_brands": [most_discounted["name"]],
            "insight_type": "pricing_strategy",
        },
        {
            "title": f"{worst['name']} has the most room for improvement",
            "description": f"With the lowest sentiment score ({worst.get('sentiment_score', 0):.2f}), {worst['name']} should focus on addressing top customer complaints to improve competitive positioning.",
            "supporting_data": [
                f"Sentiment: {worst.get('sentiment_score', 0):.2f}",
                f"Top cons: {', '.join(worst.get('top_cons', [])[:2])}",
            ],
            "affected_brands": [worst["name"]],
            "insight_type": "product_gap",
        },
    ]

    return insights
