# app/api/schemas/lab_result.py
from enum import Enum
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional

class TrendEnum(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    STABLE = "STABLE"
    NONE = "NONE"

class LabResultBase(BaseModel):
    parameter: str
    value: float
    unit: Optional[str] = None
    reference_range: Optional[str] = None


class LabStudyCreate(BaseModel):
    laboratory_name: Optional[str] = None
    test_date: date
    results: List[LabResultBase] = Field(..., min_length=1)


class LabResultResponse(LabResultBase):
    id_result: int

    class Config:
        from_attributes = True


class LabStudyResponse(BaseModel):
    id_study: int
    laboratory_name: Optional[str] = None
    test_date: date
    created_at: datetime
    results: List[LabResultResponse]

    class Config:
        from_attributes = True


# Para el endpoint de evolución longitudinal por parámetro
class ParameterDataPoint(BaseModel):
    test_date: date
    value: float
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    laboratory_name: Optional[str] = None
    id_study: int
    trend: Optional[TrendEnum] = TrendEnum.NONE  # Se calculará en el endpoint

    class Config:
        from_attributes = True


class ParameterEvolutionResponse(BaseModel):
    parameter: str
    data_points: List[ParameterDataPoint]

class LabStudyUpdate(BaseModel):
    laboratory_name: Optional[str] = None
    test_date: Optional[date] = None

class LabResultUpdate(BaseModel):
    parameter: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None