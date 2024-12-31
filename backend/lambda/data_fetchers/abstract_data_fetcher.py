from abc import ABC, abstractmethod
from typing import List

class WTKDataFetcher(ABC):
    """
    Abstract class for fetching data from the WTK API
    """
    def __init__(self):
        """
        Add default settings, configurations, etc.
        """
        pass

    @abstractmethod
    def fetch_data(self, lat: float, lon: float, height: List[int], yearly: bool = False):
        """
        Data fetching method specifications:
        
        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            height (List[int]): List of heights in integer
            yearly (bool): Boolean flag to indicate to return yearly averaged data or latest row of data
        """
        pass