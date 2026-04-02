from fastapi import APIRouter, Query
from backend.config import load_json

router = APIRouter()


@router.get("/insights")
def get_insights():
    return load_json("insights.json")


@router.get("/anomalies")
def get_anomalies(
    brand: str | None = Query(None),
    severity: str | None = Query(None),
):
    anomalies = load_json("anomalies.json")
    if brand:
        anomalies = [a for a in anomalies if a["brand"] == brand]
    if severity:
        anomalies = [a for a in anomalies if a["severity"] == severity]
    return anomalies


@router.get("/aspects")
def get_aspects(brand: str | None = Query(None)):
    aspects = load_json("aspect_sentiments.json")
    if brand:
        aspects = [a for a in aspects if a["brand"] == brand]
    return aspects


@router.get("/value-for-money")
def get_value_for_money():
    return load_json("value_for_money.json")


@router.get("/trust-signals")
def get_trust_signals():
    return load_json("trust_signals.json")
