from typing import List
from .abstract_data_fetcher import WTKDataFetcher
from ..app.utils.data_fetcher_utils import generate_key

class DatabaseDataFetcher(WTKDataFetcher):
    """
    Class for fetching data from the database.
    TODO: Refactor this to handle pre-computed/aggregated results in the future instead of caching.
    """
    def __init__(self, db_manager):
        """
        Initializes the DatabaseDataFetcher with the given DatabaseManager.
        
        Args:
            db_manager (DatabaseManager): The DatabaseManager to use for fetching data.
        """
        self.db_manager = db_manager

    def fetch_data(self, lat: float, lon: float, height: List[int], yearly: bool = False):
        """
        Fetch data from the database.

        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            height (List[int]): List of heights in integer
            yearly (bool): Boolean flag to indicate to return yearly averaged data or latest row of data

        Returns:
            dict: The data associated with the key, or None if the key does not exist.
        """
        key = self.generate_key(lat, lon, height, yearly)
        data = self.db_manager.get_data(key)
        if data:
            self.store_data(key, data)
        return data if data else None

    def store_data(self, key, data):
        """
        Store data in the database.
        
        Args:
            key (str): The key associated with the data.
            data (str): The data to be stored.
        """
        self.db_manager.store_data(key, data)