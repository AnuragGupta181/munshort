"""Gemini-powered sentiment analysis for reviews."""

import json
import os

from google import genai


BATCH_SIZE = 15

SENTIMENT_PROMPT = """Analyze the following customer reviews for a luggage product. For each review, provide:
1. sentiment_score: a float from -1.0 (very negative) to 1.0 (very positive)
2. sentiment_label: one of "very_negative", "negative", "neutral", "positive", "very_positive"
3. themes: list of 1-3 key themes mentioned (e.g., "durability", "wheel quality", "value for money")

Also provide a batch summary with:
- top_positive_themes: top 3 positive themes across all reviews
- top_negative_themes: top 3 negative themes across all reviews
- overall_sentiment: average sentiment score

Return ONLY valid JSON in this exact format:
{
  "reviews": [
    {"index": 0, "sentiment_score": 0.7, "sentiment_label": "positive", "themes": ["durability", "design"]},
    ...
  ],
  "summary": {
    "top_positive_themes": ["theme1", "theme2", "theme3"],
    "top_negative_themes": ["theme1", "theme2", "theme3"],
    "overall_sentiment": 0.4
  }
}

Reviews to analyze:
"""


def get_client():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment")
    return genai.Client(api_key=api_key)


def analyze_reviews_batch(reviews: list[dict]) -> dict:
    """Send a batch of reviews to Gemini for sentiment analysis."""
    client = get_client()

    review_text = "\n".join(
        f"[{i}] Rating: {r.get('rating', 'N/A')}/5 | Title: {r.get('title', '')} | Body: {r.get('body', '')}"
        for i, r in enumerate(reviews)
    )

    prompt = SENTIMENT_PROMPT + review_text

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            text = response.text.strip()
            # Extract JSON from response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            return json.loads(text)
        except (json.JSONDecodeError, Exception) as e:
            if attempt < 2:
                import time
                time.sleep(2 ** (attempt + 1))
                continue
            print(f"    Warning: Gemini analysis failed after 3 attempts: {e}")
            return _fallback_sentiment(reviews)

    return _fallback_sentiment(reviews)


def analyze_all_reviews(reviews: list[dict]) -> list[dict]:
    """Analyze all reviews in batches."""
    enriched = []

    for i in range(0, len(reviews), BATCH_SIZE):
        batch = reviews[i:i + BATCH_SIZE]
        print(f"    Analyzing reviews {i+1}-{i+len(batch)} of {len(reviews)}...")

        result = analyze_reviews_batch(batch)
        review_results = result.get("reviews", [])

        for j, review in enumerate(batch):
            analysis = next(
                (r for r in review_results if r.get("index") == j),
                None,
            )
            if analysis:
                review["sentiment_score"] = analysis.get("sentiment_score", 0.0)
                review["sentiment_label"] = analysis.get("sentiment_label", "neutral")
                review["aspects_mentioned"] = analysis.get("themes", [])
            else:
                # Fallback based on rating
                review["sentiment_score"] = _rating_to_sentiment(review.get("rating", 3))
                review["sentiment_label"] = _score_to_label(review["sentiment_score"])
                review["aspects_mentioned"] = []

            enriched.append(review)

    return enriched


def generate_review_synthesis(reviews: list[dict], brand: str) -> str:
    """Generate a short synthesis paragraph for a set of reviews."""
    if not reviews:
        return "No reviews available."

    try:
        client = get_client()
        review_text = "\n".join(
            f"- {r.get('title', '')}: {r.get('body', '')[:200]}"
            for r in reviews[:20]
        )
        prompt = (
            f"Write a 2-3 sentence synthesis of these customer reviews for a {brand} luggage product. "
            f"Highlight key positives and negatives. Be objective.\n\n{review_text}"
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception:
        avg_sentiment = sum(r.get("sentiment_score", 0) for r in reviews) / len(reviews)
        tone = "positive" if avg_sentiment > 0.3 else "mixed" if avg_sentiment > -0.1 else "negative"
        return f"Customer feedback for this {brand} product is generally {tone} based on {len(reviews)} reviews."


def _fallback_sentiment(reviews: list[dict]) -> dict:
    """Fallback sentiment using rating-based heuristic."""
    results = []
    for i, r in enumerate(reviews):
        score = _rating_to_sentiment(r.get("rating", 3))
        results.append({
            "index": i,
            "sentiment_score": score,
            "sentiment_label": _score_to_label(score),
            "themes": [],
        })
    scores = [r["sentiment_score"] for r in results]
    return {
        "reviews": results,
        "summary": {
            "top_positive_themes": [],
            "top_negative_themes": [],
            "overall_sentiment": sum(scores) / len(scores) if scores else 0,
        },
    }


def _rating_to_sentiment(rating: int) -> float:
    mapping = {1: -0.8, 2: -0.4, 3: 0.0, 4: 0.4, 5: 0.8}
    return mapping.get(rating, 0.0)


def _score_to_label(score: float) -> str:
    if score > 0.5:
        return "very_positive"
    if score > 0.1:
        return "positive"
    if score > -0.1:
        return "neutral"
    if score > -0.5:
        return "negative"
    return "very_negative"
