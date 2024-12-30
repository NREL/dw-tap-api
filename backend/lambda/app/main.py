from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import utils.random_message as random_message_fn
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

@app.get("/")
def read_root():
    return {"Hello": "World"}

# we can build each endpoint as a function in a sibling file, import and use it this way
@app.get("/random-message")
def random_message():
    # call a function in a sibling file (one that might have our data processing package)
    message = random_message_fn()
    return {"message": message}

@app.get("/random")
def random_message():
    response = requests.get('https://api.chucknorris.io/jokes/random')
    joke = response.json().get('value')
    return {"joke": joke}

@app.get("/random/{category}")
def random_message_category(category: str):
    response = requests.get(f'https://api.chucknorris.io/jokes/random?category={category}')
    joke = response.json().get('value')
    return {"joke": joke}

@app.get("/weather/{lat}/{lng}")
def get_weather(lat: float, lng: float):
    response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=auto')
    daily = response.json().get("daily")
    return [
        {"date": date, "max": max_temp, "min": min_temp} for date, max_temp, min_temp in zip(daily.get("time"), daily.get("temperature_2m_max"), daily.get("temperature_2m_min"))
    ]

@app.get("/windspeed")
def get_windspeed(lat: float, lng: float):
    print(f"Getting wind speed for {lat}, {lng}")
    return {
        "winddataexample": [
            {
                "title": "Average Wind Speed",
                "subheader": "The measured average wind speed at the location",
                "data": "4.9 m/s",
                "details": ["Detail 1", "Detail 2", "Detail 3"],
            },
            {
                "title": "Wind Resource",
                "subheader": "Estimated wind resource level",
                "data": "Moderate",
                "details": ["Detail 1", "Detail 2", "Detail 3"],
            },
            {
                "title": "Production",
                "subheader": "Estimated production potential",
                "data": "96,000 kWh/year",
                "details": ["Detail 1", "Detail 2", "Detail 3"],
            },
        ],
    }

handler = Mangum(app)
