from fastapi.testclient import TestClient
from app.main import app
# from unittest.mock import patch

client = TestClient(app)

# uncomment these when i can get local athena_config working
"""
# this patches the fetch_data method on the data_fetcher_router instance
def test_get_wtk_data_success():
    # Fake data to be returned by the mocked fetch_data call.
    fake_data = {"global_avg": 5.5}
    # Patch the fetch_data method on the data_fetcher_router instance.
    with patch("app.controllers.wind_data_controller.data_fetcher_router.fetch_data", return_value=fake_data):
        response = client.get("/wtk-data?lat=40.0&lng=-70.0&height=10&source=athena")
        assert response.status_code == 200
        assert response.json() == fake_data

# this patches the fetch_data method on the data_fetcher_router instance
def test_get_wtk_data_failure():
    # Patch the fetch_data method on the data_fetcher_router instance to raise an exception.
    with patch("app.controllers.wind_data_controller.data_fetcher_router.fetch_data", side_effect=Exception("Test exception")):
        response = client.get("/wtk-data?lat=40.0&lng=-70.0&height=10&source=athena")
        assert response.status_code == 500
        assert response.json() == {"detail": "Test exception"}
"""


def test_get_wtk_data_success():
    response = client.get("/wtk/windspeed?lat=40.0&lng=-70.0&height=10&source=athena")
    assert response.status_code == 200
    json = response.json()
    assert "global_avg" in json


def test_get_available_power_curves():
    response = client.get("/wtk/available-powercurves")
    assert response.status_code == 200
    json = response.json()
    assert "available_power_curves" in json


def test_get_windspeed_timeseries_all():
    """Test retrieving all time series data"""
    response = client.get("/wtk/windspeed-timeseries?lat=40.0&lng=-70.0&height=100")
    assert response.status_code == 200
    json = response.json()
    
    # Check that all time periods are included
    assert "yearly_avg" in json
    assert "monthly_avg" in json
    assert "hourly_avg" in json
    
    # Check data structure
    assert len(json["yearly_avg"]) > 0
    assert len(json["monthly_avg"]) == 12
    assert len(json["hourly_avg"]) == 24
    
    # Check a sample of the data
    yearly_sample = json["yearly_avg"][0]
    assert "year" in yearly_sample
    assert "windspeed_100m" in yearly_sample
    
    monthly_sample = json["monthly_avg"][0]
    assert "month" in monthly_sample
    assert "windspeed_100m" in monthly_sample
    
    hourly_sample = json["hourly_avg"][0]
    assert "hour" in hourly_sample
    assert "windspeed_100m" in hourly_sample

def test_get_windspeed_timeseries_yearly():
    """Test retrieving yearly time series data"""
    response = client.get("/wtk/windspeed-timeseries/yearly?lat=40.0&lng=-70.0&height=100")
    assert response.status_code == 200
    json = response.json()
    
    # Check that only yearly data is included
    assert "yearly_avg" in json
    assert "monthly_avg" not in json
    assert "hourly_avg" not in json
    
    # Check data structure
    assert len(json["yearly_avg"]) > 0
    
    # Check a sample of the data
    yearly_sample = json["yearly_avg"][0]
    assert "year" in yearly_sample
    assert "windspeed_100m" in yearly_sample

def test_get_windspeed_timeseries_monthly():
    """Test retrieving monthly time series data"""
    response = client.get("/wtk/windspeed-timeseries/monthly?lat=40.0&lng=-70.0&height=100")
    assert response.status_code == 200
    json = response.json()
    
    # Check that only monthly data is included
    assert "yearly_avg" not in json
    assert "monthly_avg" in json
    assert "hourly_avg" not in json
    
    # Check data structure
    assert len(json["monthly_avg"]) == 12
    
    # Check a sample of the data
    monthly_sample = json["monthly_avg"][0]
    assert "month" in monthly_sample
    assert "windspeed_100m" in monthly_sample

def test_get_windspeed_timeseries_hourly():
    """Test retrieving hourly time series data"""
    response = client.get("/wtk/windspeed-timeseries/hourly?lat=40.0&lng=-70.0&height=100")
    assert response.status_code == 200
    json = response.json()
    
    # Check that only hourly data is included
    assert "yearly_avg" not in json
    assert "monthly_avg" not in json
    assert "hourly_avg" in json
    
    # Check data structure
    assert len(json["hourly_avg"]) == 24
    
    # Check a sample of the data
    hourly_sample = json["hourly_avg"][0]
    assert "hour" in hourly_sample
    assert "windspeed_100m" in hourly_sample

def test_get_windspeed_timeseries_invalid_period():
    """Test retrieving data with an invalid time period"""
    response = client.get("/wtk/windspeed-timeseries/invalid?lat=40.0&lng=-70.0&height=100")
    assert response.status_code == 400
    assert "time_period must be one of: yearly, monthly, hourly" in response.json()["detail"]

def test_get_windspeed_timeseries_missing_params():
    """Test retrieving data with missing parameters"""
    response = client.get("/wtk/windspeed-timeseries/yearly")
    assert response.status_code == 422  # FastAPI validation error 