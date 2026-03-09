"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# --- Enums ---

class SourceType(str, Enum):
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    BLUESKY = "bluesky"


class ScheduleType(str, Enum):
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


# --- Source Configuration ---

class SourceParams(BaseModel):
    """Source-specific parameters. Each source type uses different fields."""
    subreddit: Optional[str] = None  # Reddit only
    url: Optional[str] = None  # HackerNews feed URL
    # Bluesky has no special params — uses global keywords


class SourceConfigCreate(BaseModel):
    type: SourceType
    name: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    use_global_keywords: bool = True
    params: SourceParams = Field(default_factory=SourceParams)


class SourceConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None
    use_global_keywords: Optional[bool] = None
    params: Optional[SourceParams] = None


class SourceConfigResponse(BaseModel):
    id: str
    type: SourceType
    name: str
    enabled: bool
    use_global_keywords: bool
    params: SourceParams
    created_at: Optional[datetime] = None


# --- User Settings ---

class ScheduleConfig(BaseModel):
    type: ScheduleType = ScheduleType.MANUAL
    interval_hours: Optional[int] = Field(None, ge=1, le=168)  # For hourly
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # For weekly (0=Mon)
    hour_of_day: Optional[int] = Field(None, ge=0, le=23)  # For daily/weekly


class UserSettingsUpdate(BaseModel):
    global_keywords: Optional[List[str]] = None
    time_window_hours: Optional[int] = Field(None, ge=1, le=168)
    max_trends_per_source: Optional[int] = Field(None, ge=1, le=50)
    schedule: Optional[ScheduleConfig] = None


class UserSettingsResponse(BaseModel):
    global_keywords: List[str] = Field(default_factory=list)
    time_window_hours: int = 3
    max_trends_per_source: int = 3
    result_retention_days: int = 15
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)


# --- Extraction ---

class ExtractionRequest(BaseModel):
    """Optional overrides for a single extraction run."""
    time_window_hours: Optional[int] = Field(None, ge=1, le=168)
    max_trends_per_source: Optional[int] = Field(None, ge=1, le=50)
    use_keywords: Optional[bool] = None


class ExtractionRunResponse(BaseModel):
    run_id: str
    status: str = "completed"
    results_count: int
    results: List["TrendResultResponse"]


# --- Trend Results ---

class TrendResultResponse(BaseModel):
    id: str
    source: str
    source_type: SourceType
    title: str
    url: str
    description: str = ""
    trend_score: float
    ups: int = 0
    comments: int = 0
    created_at: Optional[datetime] = None
    run_id: Optional[str] = None


class ResultsListResponse(BaseModel):
    results: List[TrendResultResponse]
    total: int
    page: int = 1
    page_size: int = 50


# --- Admin ---

class AdminConfig(BaseModel):
    source_weights: Dict[str, float] = Field(default_factory=lambda: {
        "reddit": 1.0,
        "hackernews": 1.0,
        "bluesky": 1.0,
    })
    default_retention_days: int = 15


class AdminConfigUpdate(BaseModel):
    source_weights: Optional[Dict[str, float]] = None
    default_retention_days: Optional[int] = Field(None, ge=1, le=365)


# Rebuild forward references
ExtractionRunResponse.model_rebuild()
