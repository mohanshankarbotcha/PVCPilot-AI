from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReportRequest(BaseModel):
    report_type: str  # 'daily_production', 'weekly_summary', 'monthly_financial', 'executive'
    format: str  # 'pdf', 'excel', 'csv'
    start_date: datetime
    end_date: datetime
    metrics: Optional[List[str]] = []

class ReportScheduleRequest(BaseModel):
    report_type: str
    frequency: str  # 'daily', 'weekly', 'monthly'
    recipients: List[str]
    time: str = "23:59"
