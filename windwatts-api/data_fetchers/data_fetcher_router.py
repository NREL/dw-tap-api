import json
from .abstract_data_fetcher import WTKDataFetcher

class DataFetcherRouter:
    def __init__(self):
        """
        Initializes the DataFetcherRouter.
        """
        self.fetchers = {}

    def register_fetcher(self, fetcher_name: str, fetcher: WTKDataFetcher):
        """
        Register a data fetcher with the router.

        Args:
            fetcher_name (str): The name of the fetcher.
            fetcher: The fetcher object.
        """
        self.fetchers[fetcher_name] = fetcher

    def fetch_data(self, params: dict, source: str = "athena"):
        """
        Fetch data using specified data fetcher.

        Args:
            params (dict): The parameters to pass to the fetcher, including
                lat (float): Latitude of the location
                lng (float): Longitude of the location
                height (int): Heights in meters
            source (str): The name of the fetcher to use

        Returns:
            dict: The fetched data as a dictionary.
        """
        fetcher = self.fetchers.get(source)
        if fetcher:
            return fetcher.fetch_data(**params)
        return {}

    def fetch_data_routing(self, params: dict):
        """
        Fetch data using the appropriate data fetcher through routing logics.

        Args:
            params (dict): The parameters to pass to the fetcher, including
                lat (float): Latitude of the location
                lng (float): Longitude of the location
                height (int): Heights in meters

        Returns:
            dict: The fetched data as a dictionary.
        """
        data = {}
        
        db_fetcher_available = True if "database" in self.data_fetchers else False
        s3_fetcher_available = True if "s3" in self.data_fetchers else False
        athena_fetcher_available = True if "athena" in self.data_fetchers else False

        if db_fetcher_available:
            # 1. Fetch cached data from the database
            cached_data = self.fetchers["database"].fetch_data(**params)
            if cached_data:
                return cached_data

        if athena_fetcher_available and self.is_complex_query(params):
            # 2. Fetch data from Athena
            data = self.fetchers["athena"].fetch_data(**params)
        elif s3_fetcher_available:
            # 3. Fetch data from S3
            data = self.fetchers["s3"].fetch_data(**params)

        if db_fetcher_available and not cached_data and data:
            # Store the fetched data in the database
            self.fetchers["database"].store_data(**params, data=json.dumps(data))
        return data

    @staticmethod
    def is_complex_query(params: dict) -> bool:
        """
        Determine if the query is complex.

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            height (List[int]): List of heights in meters.
            yearly (bool): Whether to fetch yearly averaged data.

        Returns:
            bool: True if the query is complex, False otherwise.
        """
        # Implement logic to determine if the query is complex
        # For example, if the query spans multiple files or requires aggregation
        return True