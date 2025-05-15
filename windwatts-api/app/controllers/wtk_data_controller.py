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

# # Initialize DataFetcherRouter and register fetchers
data_fetcher_router = DataFetcherRouter()
data_fetcher_router.register_fetcher("database", db_data_fetcher)
data_fetcher_router.register_fetcher("s3", s3_data_fetcher)
data_fetcher_router.register_fetcher("athena", athena_data_fetcher)

# Load power curves
power_curve_manager = PowerCurveManager("./app/power_curve/powercurves")

# Multiple average types for wind speed
wind_speed_avg_types = ["global", "monthly", "monthly", "hourly"]


@router.get("/windspeed/{avg_type}", summary="Retrieve wind speed with avg type - wtk data")
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


@router.get("/available-powercurves", summary="Fetch all available power curves")
def fetch_available_powercurves():
    '''
    returns available power curves
    '''
    return {'available_power_curves': list(power_curve_manager.power_curves.keys())}


@router.get("/energy-production/{time_period}", summary="Get yearly and monthly energy production estimate and average windspeed for a location at a height with a selected power curve")
@router.get("/energy-production", summary="Get global energy production estimate for a location at a height with a selected power curve")
def energy_production(lat: float, lng: float, height: int,
                               selected_powercurve: str,
                               time_period: str = None,
                               source: str = "athena"):
    """
    Fetches the global, yearly and monthly energy production and average windspeed for a given location, height, and power curve.
    Args:
        lat (float): Latitude of the location.
        lng (float): Longitude of the location.
        height (int): Height in meters.
        time_period (str, optional): Time period to retrieve. Must be one of: yearly and monthly.
                                   If not provided, returns energy production for all time.
        source (str): Source of the data. Must be one of: athena, s3, database.
    Returns:
        A JSON object containing average windspeeds and energy production at specified time period or global energy production when time period is not specified.
    """
    try:
        params = {
                "lat": lat,
                "lng": lng,
                "height": height,
                "avg_type" : "none"
                }
        # Retrieves full dataframe for a specific location from s3
        df = data_fetcher_router.fetch_data(params,source=source)
        if df is None:
            raise HTTPException(status_code=404, detail="Data not found")
        
         # If a specific time period is requested, return only that data
        if time_period:
            if time_period not in ["yearly", "monthly"]:
                raise ValueError(f"time_period must be one of: yearly, monthly")
            if time_period == 'yearly':
                yearly_avg_energy_production = power_curve_manager.fetch_yearly_avg_energy_production(df,height,selected_powercurve)
                return {'yearly_avg_energy_production' : yearly_avg_energy_production}
            elif time_period == 'monthly':
                monthly_avg_energy_production = power_curve_manager.fetch_monthly_avg_energy_production(df,height,selected_powercurve)
                return {'monthly_avg_energy_production' : monthly_avg_energy_production}
        else:
            yearly_avg_energy_production = power_curve_manager.fetch_yearly_avg_energy_production(df,height,selected_powercurve)
            return {"energy_production" : yearly_avg_energy_production['Average year']['kWh produced']}
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

