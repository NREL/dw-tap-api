from fastapi import APIRouter, HTTPException

# commented out the data functions until I can get local athena_config working
from app.config_manager import ConfigManager
from app.data_fetchers.s3_data_fetcher import S3DataFetcher
from app.data_fetchers.athena_data_fetcher import AthenaDataFetcher
from app.data_fetchers.database_data_fetcher import DatabaseDataFetcher
from app.data_fetchers.data_fetcher_router import DataFetcherRouter
from app.database_manager import DatabaseManager

from app.power_curve.power_curve_manager import PowerCurveManager

router = APIRouter()

# Initialize ConfigManager
config_manager = ConfigManager(
    secret_arn_env_var="WINDWATTS_DATA_CONFIG_SECRET_ARN",
    local_config_path="./app/config/windwatts_data_config.json") # replace with YOUR local config path
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

# Load power curves
power_curve_manager = PowerCurveManager("./app/power_curve/powercurves")

# Multiple average types for wind speed
wind_speed_avg_types = ["global", "monthly", "monthly"]


# @router.get("/windspeed/{avg_type}", summary="Retrieve wind speed with avg type - wtk data")
@router.get("/windspeed", summary="Retrieve wind speed with default global avg - wtk data")
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
    

@router.get("/available_powercurves", summary="Fetch all available power curves")
def fetch_available_powercurves():
    "returns available power curves"
    return {'available_power_curves': list(power_curve_manager.power_curves.keys())}
    

@router.get("/energy_production", summary="Get energy production for a location at a height with a selected power curve")
def energy_production(lat: float, lng: float, height: int, 
                               selected_powercurve: str, 
                               source: str = "athena"):
    params = {
            "lat": lat,
            "lng": lng,
            "height": None,
            "avg_type" : None,
            "get_df": True
            }
    # Retrieves full dataframe for a specific location from s3
    df = data_fetcher_router.fetch_data(params,source=source)
    '''
    energy production df contains these columns [year  mohr  month  hour windspeed_{height}m  windspeed_{height}m_kw  winddirection_{height}m] for given height.
    '''
    energy_production_df = power_curve_manager.fetch_energy_production_df(df, height, selected_powercurve)
    print(f"nrel-reference-{selected_powercurve}-kW")

    yearly_avg_energy_production = power_curve_manager.fetch_yearly_avg_energy_production(energy_production_df,height)
    
    return {"energy_production": yearly_avg_energy_production.loc['Average year','kWh produced']}

