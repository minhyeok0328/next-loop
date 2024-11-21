# api/models.py
from pydantic import BaseModel
from typing import List

class PredictionInput(BaseModel):
    pclass: int
    age: float
    fare: float
    sex: int  # 0: male, 1: female

class PredictionOutput(BaseModel):
    survival_probability: float
    prediction: int
    version: str

