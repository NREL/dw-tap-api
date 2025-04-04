import random
from fastapi import APIRouter, HTTPException

# commented out the data functions until I can get local athena_config working
# from app.config_manager import ConfigManager
# from app.data_fetchers.s3_data_fetcher import S3DataFetcher
# from app.data_fetchers.athena_data_fetcher import AthenaDataFetcher
# from app.data_fetchers.database_data_fetcher import DatabaseDataFetcher
# from app.data_fetchers.data_fetcher_router import DataFetcherRouter
# from app.database_manager import DatabaseManager

from app.power_curve.power_curve_manager import PowerCurveManager

router = APIRouter()

# # Initialize ConfigManager
# config_manager = ConfigManager(
#     secret_arn_env_var="WINDWATTS_DATA_CONFIG_SECRET_ARN",
#     local_config_path="./app/config/windwatts_data_config.json") # replace with YOUR local config path
# athena_config = config_manager.get_config()

# # Initialize DataFetchers
# s3_data_fetcher = S3DataFetcher("WINDWATTS_S3_BUCKET_NAME")
# athena_data_fetcher = AthenaDataFetcher(athena_config=athena_config)
# db_manager = DatabaseManager()
# db_data_fetcher = DatabaseDataFetcher(db_manager=db_manager)

# # Initialize DataFetcherRouter and register fetchers
# data_fetcher_router = DataFetcherRouter()
# data_fetcher_router.register_fetcher("database", db_data_fetcher)
# data_fetcher_router.register_fetcher("s3", s3_data_fetcher)
# data_fetcher_router.register_fetcher("athena", athena_data_fetcher)

# Load power curves
power_curve_manager = PowerCurveManager("./app/power_curve/powercurves")

# Multiple average types for wind speed
wind_speed_avg_types = ["global", "yearly", "monthly", "hourly"]


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

        # random data with 2 decimal places
        average = round(random.uniform(1, 8), 2)

        data = {
            "global_avg": average,
        }

        # data = data_fetcher_router.fetch_data(params, source=source)
        if data is None:
            raise HTTPException(status_code=404, detail="Data not found")
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/windspeed-timeseries/{time_period}", summary="Retrieve detailed wind speed time series data for a specific time period")
@router.get("/windspeed-timeseries", summary="Retrieve all wind speed time series data")
def get_windspeed_timeseries(
    lat: float, 
    lng: float, 
    height: int, 
    time_period: str = None, 
    source: str = "athena"
):
    '''
    Retrieve detailed wind speed time series data from the WTK database.
    Args:
        lat (float): Latitude of the location.
        lng (float): Longitude of the location.
        height (int): Height in meters.
        time_period (str, optional): Time period to retrieve. Must be one of: yearly, monthly, hourly.
                                   If not provided, returns all time periods.
        source (str): Source of the data. Must be one of: athena, s3, database.
    Returns:
        A JSON object containing wind speed data for the specified time period(s).
    '''
    try:
        params = {
            "lat": lat,
            "lng": lng,
            "height": height,
        }

        # For now, return mock data until the data fetcher is properly configured
        # In production, this would be replaced with:
        # data = data_fetcher_router.fetch_data(params, source=source)
        
        # Mock data structure for UI data table
        mock_data = {
            "yearly_avg": [
                {"year": 2001, "windspeed_100m": 8.43},
                {"year": 2002, "windspeed_100m": 8.6},
                {"year": 2003, "windspeed_100m": 9.08},
                {"year": 2004, "windspeed_100m": 8.53},
                {"year": 2005, "windspeed_100m": 8.5},
                {"year": 2006, "windspeed_100m": 8.56},
                {"year": 2007, "windspeed_100m": 8.6},
                {"year": 2008, "windspeed_100m": 9.18},
                {"year": 2009, "windspeed_100m": 9.47},
                {"year": 2010, "windspeed_100m": 8.9},
                {"year": 2011, "windspeed_100m": 9.35},
                {"year": 2012, "windspeed_100m": 8.81},
                {"year": 2013, "windspeed_100m": 8.61},
                {"year": 2014, "windspeed_100m": 9.64},
                {"year": 2015, "windspeed_100m": 8.0},
                {"year": 2016, "windspeed_100m": 8.85},
                {"year": 2017, "windspeed_100m": 9.65},
                {"year": 2018, "windspeed_100m": 9.11},
                {"year": 2019, "windspeed_100m": 9.14},
                {"year": 2020, "windspeed_100m": 9.04}
            ],
            "monthly_avg": [
                {"month": 1, "windspeed_100m": 10.16},
                {"month": 2, "windspeed_100m": 10.52},
                {"month": 3, "windspeed_100m": 10.43},
                {"month": 4, "windspeed_100m": 9.86},
                {"month": 5, "windspeed_100m": 8.37},
                {"month": 6, "windspeed_100m": 7.91},
                {"month": 7, "windspeed_100m": 6.34},
                {"month": 8, "windspeed_100m": 6.58},
                {"month": 9, "windspeed_100m": 7.11},
                {"month": 10, "windspeed_100m": 8.75},
                {"month": 11, "windspeed_100m": 10.08},
                {"month": 12, "windspeed_100m": 10.72}
            ],
            "hourly_avg": [
                {"hour": 1, "windspeed_100m": 8.45},
                {"hour": 2, "windspeed_100m": 8.71},
                {"hour": 3, "windspeed_100m": 9.02},
                {"hour": 4, "windspeed_100m": 9.28},
                {"hour": 5, "windspeed_100m": 9.44},
                {"hour": 6, "windspeed_100m": 9.48},
                {"hour": 7, "windspeed_100m": 9.5},
                {"hour": 8, "windspeed_100m": 9.54},
                {"hour": 9, "windspeed_100m": 9.64},
                {"hour": 10, "windspeed_100m": 9.78},
                {"hour": 11, "windspeed_100m": 9.84},
                {"hour": 12, "windspeed_100m": 9.89},
                {"hour": 13, "windspeed_100m": 9.94},
                {"hour": 14, "windspeed_100m": 9.83},
                {"hour": 15, "windspeed_100m": 9.14},
                {"hour": 16, "windspeed_100m": 8.4},
                {"hour": 17, "windspeed_100m": 7.88},
                {"hour": 18, "windspeed_100m": 7.74},
                {"hour": 19, "windspeed_100m": 7.79},
                {"hour": 20, "windspeed_100m": 7.92},
                {"hour": 21, "windspeed_100m": 8.06},
                {"hour": 22, "windspeed_100m": 8.13},
                {"hour": 23, "windspeed_100m": 8.1},
                {"hour": 24, "windspeed_100m": 8.16}
            ]
        }
        
        # If a specific time period is requested, return only that data
        if time_period:
            if time_period not in ["yearly", "monthly", "hourly"]:
                raise ValueError(f"time_period must be one of: yearly, monthly, hourly")
            
            # Return only the requested time period data
            return {f"{time_period}_avg": mock_data[f"{time_period}_avg"]}
        
        # Otherwise return all time periods
        return mock_data
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


@router.get("/energy-production", summary="Get energy production for a location at a height with a selected power curve")
def energy_production(lat: float, lng: float, height: int,
                               selected_powercurve: str,
                               source: str = "athena"):
    """
    Fetches the energy production for a given location, height, and power curve.
    """
    try:
        # params = {
        #     "lat": lat,
        #     "lng": lng,
        #     "height": None,
        #     "avg_type" : "none"
        # }

        df = {}

        # Retrieves full dataframe for a specific location from s3
        # df = data_fetcher_router.fetch_data(params,source=source)
        if df is None:
            raise HTTPException(status_code=404, detail="Data not found")

        # yearly_avg_energy_production = power_curve_manager.fetch_yearly_avg_energy_production(df,height,selected_powercurve)

        # return {"energy_production": yearly_avg_energy_production['Average year']['kWh produced']}
        return {"energy_production": random.randint(10000, 100000)} # placeholder until I can get local athena_config working
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

