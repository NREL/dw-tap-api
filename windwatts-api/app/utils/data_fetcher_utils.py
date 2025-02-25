from typing import List

def generate_key(lat: float, lon: float, height: List[int], yearly: bool) -> str:
    """
    Generate a unique key for the database based on the parameters.

    Args:
        lat (float): Latitude of the location
        lon (float): Longitude of the location
        height (List[int]): List of heights in integer
        yearly (bool): Boolean flag to indicate to return yearly averaged data or latest row of data

    Returns:
        str: A unique key for the database.
    """
    height_str = '_'.join(map(str, height))
    return f"{lat}_{lon}_{height_str}_{'yearly' if yearly else 'latest'}"