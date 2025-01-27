from .abstract_data_fetcher import WTKDataFetcher
from windwatts_data import WTKLedClient1224

class AthenaDataFetcher(WTKDataFetcher):
    def __init__(self, athena_config):
        """
        Initializes the AthenaDataFetcher with the given configuration.

        Args:
            athena_config (str): Path to the Athena configuration file.
        """
        self.wtk_client = WTKLedClient1224(config_path=athena_config)

    def fetch_data(self, lat: float, lng: float, height: int):
        """
        Fetch data from Athena using the WTKLedClient.

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            height (int): Height in meters.

        Returns:
            list: The fetched data as a list of dictionaries.
        """
        filtered_data = self.wtk_client.fetch_windwatts_data(lat=lat, lng=lng, height=height)
        return filtered_data.to_dict(orient="records")