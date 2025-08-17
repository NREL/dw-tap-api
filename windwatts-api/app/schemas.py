from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field

Numeric = Union[int, float]
ValueMap = Dict[str, Numeric]
ValueSeries = List[Numeric]
WindSpeedData = Union[Numeric, ValueMap, ValueSeries]

class WindSpeedResponse(BaseModel):
    avg_type: Literal["global", "monthly", "yearly", "hourly"]
    units: str = "m/s"
    data: WindSpeedData

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"avg_type": "global", "units": "m/s", "data": 6.2},
                {
                    "avg_type": "monthly",
                    "units": "m/s",
                    "data": {"Jan": 6.1, "Feb": 6.0, "Mar": 6.3},
                },
                {"avg_type": "yearly", "units": "m/s", "data": [6.0, 6.2, 6.3]},
            ]
        }
    }

class AvailablePowerCurvesResponse(BaseModel):
    available_power_curves: List[str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "available_power_curves": [
                    "nrel-reference-2.5kW",
                    "nrel-reference-100kW",
                ]
            }
        }
    }

class EnergyProductionResponse(BaseModel):
    energy_production: Optional[Numeric] = Field(
        default=None, description="kWh produced for the summary case"
    )
    summary_avg_energy_production: Optional[Dict[str, Dict[str, Numeric]]] = None
    yearly_avg_energy_production: Optional[Dict[str, Dict[str, Numeric]]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"energy_production": 12345.67},
                {
                    "energy_production": 12345.67,
                    "summary_avg_energy_production": {
                        "Average year": {"kWh produced": 12345.67}
                    },
                    "yearly_avg_energy_production": {
                        "2015": {"kWh produced": 1000.0},
                        "2016": {"kWh produced": 1100.0},
                    },
                },
            ]
        }
    }

class HealthCheckResponse(BaseModel):
    status: Literal["up"] = "up"

    model_config = {
        "json_schema_extra": {
            "example": {"status": "up"}
        }
    }