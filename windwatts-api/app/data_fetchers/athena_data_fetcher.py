from .abstract_data_fetcher import WTKDataFetcher
from windwatts_data import WindwattsWTKClient

class AthenaDataFetcher(WTKDataFetcher):
    def __init__(self, athena_config):
        """
        Initializes the AthenaDataFetcher with the given configuration.

        Args:
            athena_config (str): Path to the Athena configuration file.
        """
        self.wtk_client = WindwattsWTKClient(config_path=athena_config)

    def fetch_data(self, lat: float, lng: float, height: int, avg_type: str = 'global'):
        """
        Fetch data from Athena using the WTKLedClient.

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            height (int): Height in meters.

        Returns:
            dict: A dictionary containing the fetched data.
        """
        filtered_data = None
        if avg_type == 'global':
            filtered_data = self.wtk_client.fetch_global_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'yearly':
            filtered_data = self.wtk_client.fetch_yearly_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'monthly':
            filtered_data = self.wtk_client.fetch_monthly_avg_at_height(lat=lat, long=lng, height=height)
        
        return filtered_data