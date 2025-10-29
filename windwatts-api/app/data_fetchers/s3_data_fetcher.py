from typing import List, Optional
import boto3
import pandas as pd
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.config import Config
from .abstract_data_fetcher import AbstractDataFetcher

from windwatts_data import ClientBase
from app.config_manager import ConfigManager

# Initialize ConfigManager
config_manager = ConfigManager(
    secret_arn_env_var="WINDWATTS_DATA_CONFIG_SECRET_ARN",
    local_config_path="./app/config/windwatts_data_config.json")

athena_config = config_manager.get_config()

MIN_POOL_WORKERS = 1

class S3DataFetcher(AbstractDataFetcher):
    def __init__(self, bucket_name: str, prefix: str, grid: str):
        """
        Initializes the S3DataFetcher with the given bucket.
        Parameters:
            bucket_name (str): The s3 bucket name.
            prefix (str): The s3 prefix the specifies folder inside a bucket.
            grid (str): The grid of the data. "era5" or "wtk"
        """
        print(f"Initializing S3 Data Fetcher: bucket: {bucket_name} prefix: {prefix} grid: {grid} ...")
        self.s3_client = boto3.client(
            "s3",
            config=Config(
                retries={"max_attempts": 5, "mode": "standard"},
                tcp_keepalive=True,
            ),
        )
        self.bucket = bucket_name
        self.prefix = prefix
        self.grid = grid
        self.base_client = ClientBase(athena_config, data_family=self.grid)
    
    def find_nearest_locations(self, lat: float, lng: float, n_neighbors: int = 1):
        """
        Find one or more nearest grid locations (index, latitude, and longitude) to a given coordinate.

        :param lat: Latitude of the target location in decimal degrees.
        :type lat: float
        :param lng: Longitude of the target location in decimal degrees.
        :type lng: float
        :param n_neighbors: Number of nearest grid points to return. Defaults to 1.
        :type n_neighbors: int

        :return: 
            - If n_neighbors == 1: a list of single tuple [(index, latitude, longitude)] for the nearest grid point.  
            - If n_neighbors > 1: a list of tuples, each containing (index, latitude, longitude).
            - The list will have length n_neighbors.
        :rtype: 
            :rtype: list[tuple[str, float, float]]
        """
        if n_neighbors == 1:
            index, nearest_lat, nearest_lon = self.base_client.find_nearest_location(lat, lng)
            return [(index, nearest_lat, nearest_lon)]
        else:
            # A list of tuples where each tuple contains: (grid_index, latitude, longitude)
            tuples = self.base_client.find_n_nearest_locations(lat, lng, n_neighbors)
            return tuples
    
    def generate_s3_keys(self, lat: float, lng: float, years: List[int], n_neighbors: int) -> List[str]:
        """
        Build S3 object keys for the given location, years, and nearest grid indices.

        :param lat: Latitude of the target location.
        :param lng: Longitude of the target location.
        :param years: data of years to fetch.
        :param n_neighbors: Number of nearest grid points to include.
        :return: List of S3 object keys.
        """
        s3_keys: List[str] = []
        
        tuples = self.find_nearest_locations(lat, lng, n_neighbors)
        nearest_indexes = [str(idx) for idx, _, _ in tuples]

        for year in years:
            for index in nearest_indexes:
                # uri specific to era5 timeseries, might change for ensemble timeseries as it might not have year.
                s3_keys.append(f"{self.prefix}/year={year}/index={index}/{year}_{index}.csv.gz")
        
        return s3_keys
    
    def fetch_s3_file(self, key: str, cols: Optional[List[str]]):
        """
        Download + parse a single gzip CSV from S3.

        :param key: S3 object key.
        :param cols: Optional list of column names to load (passed to pandas.read_csv).
        :return: DataFrame or None on error.
        """
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            payload = obj["Body"].read()
            df = pd.read_csv(
                BytesIO(payload),
                compression="gzip",
                usecols=cols,
            )
            return df
        except Exception as e:
            print(f"Warning: Failed to fetch {key}: {e}")
            return None

    def fetch_data(
        self,
        lat: float,
        lng: float,
        years: List[int],
        n_neighbors: int = 1,
        cols: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Fetch data from S3 in parallel (optimized for ~5 files).

        Args:
            lat (float): Latitude of the location.
            lng (float): Longitude of the location.
            years (List[int]): Years of which the data is needed.
            n_neighbors (int): Number of nearest grid points to include.
            cols (Optional[List[str]]): Optional column subset to read.

        Returns:
            pd.DataFrame: Concatenated DataFrame across requested files (may be empty).
        """
        keys = self.generate_s3_keys(lat, lng, years, n_neighbors)
        if not keys:
            return pd.DataFrame()

        frames: List[pd.DataFrame] = []
        workers = min(MIN_POOL_WORKERS, len(keys))

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(self.fetch_s3_file, k, cols) for k in keys]
            for f in as_completed(futures):
                df = f.result()
                if df is not None and not df.empty:
                    frames.append(df)
        if not frames:
            print(f"No data found for lat={lat}, lng={lng}, years={years}")
            return pd.DataFrame()
        out = pd.concat(frames, ignore_index=True)

        return out
