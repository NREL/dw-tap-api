import os
from typing import List
import boto3
import pandas as pd
from io import StringIO
from .abstract_data_fetcher import WTKDataFetcher
from utils.data_fetcher_utils import generate_key

class S3DataFetcher(WTKDataFetcher):
    def __init__(self, bucket_env_var: str):
        """
        Initializes the S3DataFetcher with the given bucket.
        Parameters:
            bucket_env_var (str): The env var that contains S3 bucket name.
        """
        self.s3_client = boto3.client('s3')
        self.bucket = os.getenv(bucket_env_var)

    def fetch_data(self, lat: float, lon: float, height: int):
        """
        Fetch data from S3.

        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            height (int): Heights in meters

        Returns:
            dict: The fetched data
        """
        # Generate the S3 key based on the parameters
        s3_key = generate_key(lat, lon, height)

        # Fetch the data from S3
        response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
        data = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(data))
        # TODO: Convert the DataFrame to a dictionary
        return {
            "global_avg": 5.23,
            "yearly_avg": [
                {"year": 2020, "windspeed_10m": 5.23},
                {"year": 2021, "windspeed_10m": 5.34}
            ],
            "monthly_avg": [
                {"month": 1, "windspeed_10m": 5.12},
                {"month": 2, "windspeed_10m": 5.45}
            ],
            "hourly_avg": [
                {"hour": 0, "windspeed_10m": 4.98},
                {"hour": 1, "windspeed_10m": 5.10}
            ]
        }