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
    local_config_path="../config/windwatts_data_config.json") # replace with YOUR local config path
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

# Multiple average types for wind speed
wind_speed_avg_types = ["global", "monthly", "monthly"]


@router.get("/windspeed/{avg_type}", summary="Retrieve wind speed - wtk data")
def get_windspeed(lat: float, lng: float, height: int, avg_type: str = 'global', source: str = "athena"):
    '''
    Retrieve wind speed data from the WTK database.
    Args:
        lat (float): Latitude of the location.
        lng (float): Longitude of the location.
        height (int): Height in meters.
        avg_type (str): Type of average to retrieve. Must be one of: global (default), monthly, yearly.
        source (str): Source of the data. Must be one of: athena, s3, database.
    '''
    if avg_type not in wind_speed_avg_types:
        raise ValueError(f"avg_type must be one of: {wind_speed_avg_types}")
    try:
        params = {
            "lat": lat,
            "lng": lng,
            "height": height,
            "avg_type": avg_type
        }

        data = data_fetcher_router.fetch_data(params, source=source)
        if data is None:
            raise HTTPException(status_code=404, detail="Data not found")
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")