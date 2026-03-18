from pydantic import BaseModel, Field
from typing import Optional, List

class ProcessInput(BaseModel):
    temperature: float = Field(..., ge=20, le=80, description="Temperature in Celsius")
    pressure: float = Field(..., ge=0.5, le=1.5, description="Pressure in Bar")
    humidity: float = Field(..., ge=15, le=70, description="Humidity Percent")
    motor_speed: float = Field(..., ge=0, le=900, description="Motor Speed RPM")
    vibration: float = Field(..., ge=0, le=10, description="Vibration mm/s")
    flow_rate: float = Field(..., ge=0, le=10, description="Flow Rate LPM")
    compression_force: float = Field(..., ge=0, le=20, description="Compression Force kN")
    granulation_time: float = Field(16.0, ge=9, le=27)
    binder_amount: float = Field(9.0, ge=5.8, le=13.5)
    drying_temp: float = Field(59.4, ge=42, le=73)
    drying_time: float = Field(28.0, ge=15, le=48)
    machine_speed: float = Field(169.0, ge=92, le=280)
    lubricant_conc: float = Field(1.2, ge=0.4, le=2.8)

class QualityMetrics(BaseModel):
    hardness: float
    friability: float
    dissolution_rate: float
    content_uniformity: float
    disintegration_time: float
    tablet_weight: float

class EnergyMetrics(BaseModel):
    power_consumption: float
    energy_status: str
    co2_emissions: float
    efficiency_score: float

class RootCause(BaseModel):
    issue: str
    severity: str
    recommendation: str

class AnomalyInfo(BaseModel):
    detected: bool
    type: Optional[str]
    description: Optional[str]

class PredictionResponse(BaseModel):
    quality: QualityMetrics
    energy: EnergyMetrics
    root_causes: List[RootCause]
    anomaly: AnomalyInfo
    golden_deviation: Optional[dict]
    shap_importance: dict
