"""Aspect-level sentiment extraction using Gemini."""

import json
import os

from google import genai


ASPECTS = ["wheels", "handle", "material", "zipper", "size_space", "durability"]

ASPECT_PROMPT = """Analyze these customer reviews for a luggage product and extract sentiment for these specific aspects:
- wheels: wheel quality, rolling, spinning
- handle: handle durability, telescopic handle, grip
- material: fabric, shell, build quality, material type
- zipper: zipper quality, zip durability, locking mechanism
- size_space: storage capacity, compartments, expandability, size
- durability: overall durability, breakage, longevity, wear

For each aspect mentioned in the reviews, provide a sentiment score from -1.0 to 1.0.
If an aspect is not mentioned, use null.

Return ONLY valid JSON:
{
  "aspect_sentiments": {
    "wheels": 0.5,
    "handle": -0.3,
    "material": 0.2,
    "zipper": null,
    "size_space": 0.7,
    "durability": -0.1
  }
}

Reviews:
"""


def extract_aspects_for_product(reviews: list[dict]) -> dict[str, float]:
    """Extract aspect-level sentiment for a product's reviews."""
    if not reviews:
        return {a: 0.0 for a in ASPECTS}

    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return _fallback_aspects(reviews)

        client = genai.Client(api_key=api_key)

        review_text = "\n".join(
            f"- [{r.get('rating', 'N/A')}/5] {r.get('body', '')[:300]}"
            for r in reviews[:20]
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=ASPECT_PROMPT + review_text,
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)
        aspects = data.get("aspect_sentiments", {})

        # Ensure all aspects have a value
        return {a: float(aspects.get(a, 0) or 0) for a in ASPECTS}

    except Exception as e:
        print(f"    Warning: Aspect extraction failed: {e}")
        return _fallback_aspects(reviews)


def compute_brand_aspects(products_aspects: list[dict[str, float]]) -> dict[str, float]:
    """Aggregate aspect scores across products for a brand."""
    if not products_aspects:
        return {a: 0.0 for a in ASPECTS}

    result = {}
    for aspect in ASPECTS:
        scores = [pa.get(aspect, 0.0) for pa in products_aspects if pa.get(aspect) is not None]
        result[aspect] = round(sum(scores) / len(scores), 2) if scores else 0.0
    return result


def _fallback_aspects(reviews: list[dict]) -> dict[str, float]:
    """Simple keyword-based aspect detection fallback."""
    aspect_keywords = {
        "wheels": ["wheel", "roll", "spin", "caster"],
        "handle": ["handle", "grip", "telescop", "pull"],
        "material": ["material", "fabric", "shell", "build", "quality", "plastic"],
        "zipper": ["zipper", "zip", "lock", "latch"],
        "size_space": ["space", "storage", "compartment", "capacity", "size", "fit"],
        "durability": ["durable", "durability", "break", "broke", "crack", "damage", "sturdy", "last"],
    }

    aspect_scores: dict[str, list[float]] = {a: [] for a in ASPECTS}

    for review in reviews:
        body = review.get("body", "").lower()
        rating = review.get("rating", 3)
        base_score = (rating - 3) / 2  # -1 to 1 range

        for aspect, keywords in aspect_keywords.items():
            if any(kw in body for kw in keywords):
                aspect_scores[aspect].append(base_score)

    return {
        a: round(sum(scores) / len(scores), 2) if scores else 0.0
        for a, scores in aspect_scores.items()
    }
