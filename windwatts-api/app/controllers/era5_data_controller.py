'''
Placeholder for ERA5 data controller
'''

from fastapi import APIRouter


router = APIRouter()

@router.get("/windspeed", summary="Retrieve global wind speed - ERA5 data")
def get_windspeed(lat: float, lng: float, height: int):
    return {"message": "This is a placeholder for the ERA5 data controller"}