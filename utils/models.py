from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    database_url: str
    prompt: str

class InitialAnalysisResponse(BaseModel):
    database_type: str
    database_name: str
    isEmailRequired: bool
    isReportGenerationRequired: bool
    isVisualizationRequired: bool