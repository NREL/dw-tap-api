from .abstract_data_fetcher import WTKDataFetcher
from wtk_client import WTKLedClient

class AthenaDataFetcher(WTKDataFetcher):
    def __init__(self, athena_config):
        """
        Initializes the AthenaDataFetcher with the given configuration.

        Args:
            athena_config (str): Path to the Athena configuration file.
        """
        self.wtk_client = WTKLedClient(config_path=athena_config)

    def fetch_data(self, lat: float, lng: float, heights: list, yearly: bool = False):
        """
        Fetch data from Athena using the WTKLedClient.

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            heights (list): List of heights in meters.
            yearly (bool): Whether to fetch yearly averaged data.

        Returns:
            list: The fetched data as a list of dictionaries.
        """
        filtered_data = self.wtk_client.get_statistic_1224(lat=lat, lng=lng, heights=heights, yearly=yearly)
        return filtered_data.to_dict(orient="records")