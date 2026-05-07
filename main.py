import os
import requests
import redis
from fastapi import FastAPI,HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

cache = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
API_KEY = os.getenv("VISUAL_CROSSINZG_API_KEY")

@app.get("/weather/{city}")
def get_weather(city: str):
    cached_data = cache.get(city)
    if cached_data:
        return {"source": "cache", "data": cached_data}
    
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        cache.set(city, str(data), ex=43200)

        return {"source": "api", "data": data}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")
