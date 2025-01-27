from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import utils.random_message as random_message_fn
import requests
from config_manager import ConfigManager
from data_fetchers.s3_data_fetcher import S3DataFetcher
from data_fetchers.athena_data_fetcher import AthenaDataFetcher
from data_fetchers.database_data_fetcher import DatabaseDataFetcher
from data_fetchers.data_fetcher_router import DataFetcherRouter
from database_manager import DatabaseManager

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

# # Initialize ConfigManager
config_manager = ConfigManager(
    secret_arn_env_var="WINDWATTS_DATA_CONFIG_SECRET_ARN",
    local_config_path="./config/windwatts_data_config.json")
athena_config = config_manager.get_config()

# Initialize DataFetchers
s3_data_fetcher = S3DataFetcher(bucket='s3-bucket-name')  # Need the actual bucket name
athena_data_fetcher = AthenaDataFetcher(athena_config=athena_config)
db_manager = DatabaseManager()
db_data_fetcher = DatabaseDataFetcher(db_manager=db_manager)

# Initialize DataFetcherRouter and register fetchers
data_fetcher_router = DataFetcherRouter()
data_fetcher_router.register_fetcher("database", db_data_fetcher)
data_fetcher_router.register_fetcher("s3", s3_data_fetcher)
# data_fetcher_router.register_fetcher("athena", athena_data_fetcher)

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

@app.get("/wtk-data")
def get_wtk_data(lat: float, lng: float, height: List[int], yearly: bool = False, source: str = "athena"):
    try:
        params = {
            "lat": lat,
            "lng": lng,
            "height": height,
            "yearly": yearly
        }
        data = data_fetcher_router.fetch_data(params, source=source)
        if data is None:
            raise HTTPException(status_code=404, detail="Data not found")
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

handler = Mangum(app)
