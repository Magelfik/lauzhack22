import json

from fastapi import APIRouter, HTTPException, Depends

from shared import cache

router = APIRouter(
    prefix="/test"
)


@router.get("/")
def get_cache():
    data = cache
    return json.dumps(dict(cache.items()))


