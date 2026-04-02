from fastapi import APIRouter
from backend.config import load_json

router = APIRouter()


@router.get("/filters")
def get_filters():
    return load_json("filter_options.json")
