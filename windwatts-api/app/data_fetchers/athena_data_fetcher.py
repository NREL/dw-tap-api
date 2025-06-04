from .abstract_data_fetcher import AbstractDataFetcher
from windwatts_data import WindwattsWTKClient, WindwattsERA5Client

class AthenaDataFetcher(AbstractDataFetcher):
    def __init__(self, athena_config: str, data_type: str):
        """
        Initializes the AthenaDataFetcher with the given configuration.

        Args:
            athena_config (str): Path to the Athena configuration file.
            data_type (str): Type of data source ('wtk' or 'era5').
        """
        self.data_type = data_type.lower()
        if self.data_type == 'wtk':
            print("Initializing WTK Client")
            self.client = WindwattsWTKClient(config_path=athena_config)
        elif self.data_type == 'era5':
            print("Initializing ERA5 Client")
            self.client = WindwattsERA5Client(config_path=athena_config)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

    def fetch_data(self, lat: float, lng: float, height: int, avg_type: str = 'global') -> dict:
        """
        Fetch wind data using the configured client.

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            height (int): Height in meters.
            avg_type (str): Average type to fetch.
                For 'wtk': ['global', 'yearly', 'monthly', 'hourly', 'none']
                For 'era5': ['global', 'yearly', 'none']

        Returns:
            dict: Fetched wind data.

        Raises:
            ValueError: If the avg_type is not supported for the selected client.
        """
        valid_avg_types_params = {
            'wtk': ['global', 'yearly', 'monthly', 'hourly', 'none'],
            'era5': ['global', 'yearly', 'none']
        }

        if avg_type not in valid_avg_types_params[self.data_type]:
            raise ValueError(f"avg_type '{avg_type}' is not supported for data type '{self.data_type}'")

        if avg_type == 'none':
            return self.client.fetch_df(lat=lat, long=lng, height=height)
        elif avg_type == 'global':
            return self.client.fetch_global_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'yearly':
            return self.client.fetch_yearly_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'monthly':
            return self.client.fetch_monthly_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'hourly':
            return self.client.fetch_hourly_avg_at_height(lat=lat, long=lng, height=height)
        else:
            raise ValueError(f"Invalid avg_type: {avg_type}")