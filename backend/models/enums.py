from enum import Enum


class PriceBand(str, Enum):
    BUDGET = "budget"
    VALUE = "value"
    MIDRANGE = "midrange"
    PREMIUM = "premium"


class SentimentLevel(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"
