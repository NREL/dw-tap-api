from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.controllers.random_controller import router as random_router
from app.controllers.wind_data_controller import router as wind_data_router
import requests

app = FastAPI()

origins = [
    "http://localhost",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wind_data_router, tags=["winddata"])
app.include_router(random_router, prefix="/random", tags=["random"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/weather/{lat}/{lng}")
def get_weather(lat: float, lng: float):
    response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=auto')
    daily = response.json().get("daily")
    return [
        {"date": date, "max": max_temp, "min": min_temp} for date, max_temp, min_temp in zip(daily.get("time"), daily.get("temperature_2m_max"), daily.get("temperature_2m_min"))
    ]


handler = Mangum(app)
