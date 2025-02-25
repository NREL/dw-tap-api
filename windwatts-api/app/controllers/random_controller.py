'''
    This still just exists as an example...we should remove this before we go
    live
'''

import requests
from fastapi import APIRouter, HTTPException
from app.utils.random_message import random_message as get_random_message

router = APIRouter()

categories = [
    "animal",
    "career",
    "celebrity",
    "dev",
    "explicit",
    "fashion",
    "food",
    "history",
    "money",
    "movie",
    "music",
    "political",
    "religion",
    "science",
    "sport",
    "travel"
]

@router.get("/", summary="Retrieve a random message")
def read_random_message():
    try:
        message = get_random_message()
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chuck", summary="Get a random Chuck Norris joke")
def get_chuck_norris_joke():
    try:
        response = requests.get("https://api.chucknorris.io/jokes/random")
        response.raise_for_status()
        joke = response.json().get("value")
        return {"joke": joke}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching joke: {e}")

@router.get("/chuck/{category}", summary="Get a random Chuck Norris joke from a list of categories")
def get_chuck_norris_joke(category: str):
    if category not in categories:
        raise HTTPException(status_code=500, detail=f"Category can only be one of: {categories}")
    try:
        response = requests.get(f'https://api.chucknorris.io/jokes/random?category={category}')
        response.raise_for_status()
        joke = response.json().get("value")
        return {"joke": joke}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching joke: {e}")
