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
        Fetch wind data from Athena using the WTK client.

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            height (int): Height in meters.
            avg_type (str): The type of average to fetch. 
                            Accepted values are:
                            - 'global': Retrieves global average data.
                            - 'yearly': Retrieves yearly average data.
                            - 'monthly': Retrieves monthly average data.
                            - 'none': Retrieves the complete dataset (all heights).
                            Defaults to 'global'.

        Returns:
            dict: A dictionary containing the requested wind data.

        Raises:
            ValueError: If an invalid `avg_type` is provided.
        """

        filtered_data = None
            
        if avg_type == "none":
            self.wtk_client.fetch_data(lat=lat, long=lng)
            filtered_data = self.wtk_client.df
        elif avg_type == 'global':
            filtered_data = self.wtk_client.fetch_global_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'yearly':
            filtered_data = self.wtk_client.fetch_yearly_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'monthly':
            filtered_data = self.wtk_client.fetch_monthly_avg_at_height(lat=lat, long=lng, height=height)
        elif avg_type == 'hourly':
            filtered_data = self.wtk_client.fetch_hourly_avg_at_height(lat=lat, long=lng, height=height)
        else:
            raise ValueError(f"Invalid avg_type: {avg_type}")
        
        return filtered_data