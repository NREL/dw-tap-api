from typing import List
import boto3
import pandas as pd
from io import StringIO
from .abstract_data_fetcher import WTKDataFetcher
from utils.data_fetcher_utils import generate_key

class S3DataFetcher(WTKDataFetcher):
    def __init__(self, bucket: str):
        self.s3_client = boto3.client('s3')
        self.bucket = bucket

    def fetch_data(self, lat: float, lon: float, height: List[int], yearly: bool = False):
        """
        Fetch data from S3.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.
            height (List[int]): List of heights in meters.
            yearly (bool): Whether to fetch yearly averaged data.

        Returns:
            list: The fetched data as a list of dictionaries.
        """
        # Generate the S3 key based on the parameters
        s3_key = generate_key(lat, lon, height, yearly)

        # Fetch the data from S3
        response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
        data = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(data))
        return df.to_dict(orient="records")