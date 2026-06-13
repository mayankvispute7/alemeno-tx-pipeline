from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Upload Response ---
class JobCreateResponse(BaseModel):
    job_id: int
    message: str
    filename: str

    class Config:
        from_attributes = True

# --- Status Response ---
class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    filename: str
    summary_stats: Optional[Dict[str, Any]] = None

# --- Transaction Model ---
class TransactionData(BaseModel):
    id: int
    date: str
    merchant: Optional[str]
    amount: float
    currency: Optional[str]
    status: Optional[str]
    category: Optional[str]
    is_anomaly: bool
    anomaly_reason: Optional[str]

    class Config:
        from_attributes = True

# --- Full Results Response ---
class JobSummaryData(BaseModel):
    total_spend_inr: float
    total_spend_usd: float
    top_merchants: List[str]
    anomaly_count: int
    narrative: str
    risk_level: str

    class Config:
        from_attributes = True

class JobResultsResponse(BaseModel):
    job_id: int
    status: str
    filename: str
    summary: Optional[JobSummaryData]
    transactions: List[TransactionData]

# --- List Jobs Response ---
class JobListItem(BaseModel):
    job_id: int
    filename: str
    status: str
    row_count_clean: int
    created_at: datetime

    class Config:
        from_attributes = True