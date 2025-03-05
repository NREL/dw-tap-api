from fastapi import APIRouter, HTTPException

# commented out the data functions until I can get local athena_config working
from app.config_manager import ConfigManager
from app.data_fetchers.s3_data_fetcher import S3DataFetcher
from app.data_fetchers.athena_data_fetcher import AthenaDataFetcher
from app.data_fetchers.database_data_fetcher import DatabaseDataFetcher
from app.data_fetchers.data_fetcher_router import DataFetcherRouter
from app.database_manager import DatabaseManager

router = APIRouter()

# Initialize ConfigManager
config_manager = ConfigManager(
    secret_arn_env_var="WINDWATTS_DATA_CONFIG_SECRET_ARN",
    local_config_path="./config/windwatts_data_config.json")
athena_config = config_manager.get_config()

# Initialize DataFetchers
s3_data_fetcher = S3DataFetcher("WINDWATTS_S3_BUCKET_NAME")
athena_data_fetcher = AthenaDataFetcher(athena_config=athena_config)
db_manager = DatabaseManager()
db_data_fetcher = DatabaseDataFetcher(db_manager=db_manager)

# Initialize DataFetcherRouter and register fetchers
data_fetcher_router = DataFetcherRouter()
data_fetcher_router.register_fetcher("database", db_data_fetcher)
data_fetcher_router.register_fetcher("s3", s3_data_fetcher)
data_fetcher_router.register_fetcher("athena", athena_data_fetcher)


@router.get("/windspeed", summary="Retrieve wind speed data")
def get_windspeed(lat: float, lng: float):
    try:
        # data = data_fetcher_router.fetch_windspeeddata(params, source=source)
        return {
            "winddataexample": [
                {
                    "title": "Average Wind Speed",
                    "subheader": "The measured average wind speed at the location",
                    "data": f"{get_wtk_data(lat=lat, lng=lng, height=10)['global_avg']} m/s",
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/wtk-data/windspeed", summary="Retrieve WTK data")
def get_wtk_data(lat: float, lng: float, height: int, source: str = "athena"):
    try:
        params = {
            "lat": lat,
            "lng": lng,
            "height": height,
        }
        data = params
        data = data_fetcher_router.fetch_data(params, source=source)
        if data is None:
            raise HTTPException(status_code=404, detail="Data not found")
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
