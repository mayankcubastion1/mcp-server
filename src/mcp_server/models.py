from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Holiday(BaseModel):
    """Represents a holiday returned by the HRMS API."""

    holidayDate: date
    descText: str
    type: str


class HolidaysResponse(BaseModel):
    """Response model for the holidays endpoint."""

    statusCode: int
    statusMessage: str
    data: List[Holiday]
    rhBalance: Optional[int] = None


class LeaveEntry(BaseModel):
    """Represents a single leave or comp-off entry."""

    id: str = Field(alias="Id")
    category: str
    type: str
    status: str
    leaveDate: date
    leaveCount: float
    comments: Optional[str] = None
    salaryYear: Optional[str] = None
    salaryMonth: Optional[str] = None
    subStatus: Optional[str] = None
    appliedDate: date
    approvedDate: Optional[date] = None
    employeeId: str
    employeeFinancialYearId: str
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(populate_by_name=True)


class LeavesResponse(BaseModel):
    """Response model for the leaves endpoint."""

    statusCode: int
    statusMessage: str
    data: List[LeaveEntry]
