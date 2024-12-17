# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class URLInput(BaseModel):
    urls: List[str]
    analysis_type: str = "full"  # full, elon, jobs
    user_id: Optional[str] = None

class AnalysisInput(BaseModel):
    headline: str
    content: str
    industry: str
    product: str
    elon_analysis: Optional[str]
    jobs_analysis: Optional[str]
    url: Optional[str]

class AnalysisResponse(BaseModel):
    title: str
    content: str
    industry: str
    product: str
    elon_analysis: Optional[str]
    jobs_analysis: Optional[str]
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class StorageResponse(BaseModel):
    status: str
    message: str
    vector_id: Optional[str]

class HealthResponse(BaseModel):
    api: str
    services: Dict[str, str]
    timestamp: str

class ErrorResponse(BaseModel):
    detail: str