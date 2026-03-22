"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# --- Enums ---


class ScheduleType(str, Enum):
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


# --- Source Catalog ---


class SourceCatalogEntry(BaseModel):
    """Represents a source definition in the top-level catalog."""

    id: str
    name: str
    description: str = ""
    icon: str = ""
    website_url: str = ""
    category: str = "general"
    supports_keywords: bool = True
    is_multi_instance: bool = False
    visibility: str = "public"  # "disabled" | "public" | "beta" | "pro"
    config_schema: Dict[str, Any] = Field(default_factory=dict)
    default_params: Dict[str, Any] = Field(default_factory=dict)


# --- Source Configuration (User Subscriptions) ---


class SourceConfigCreate(BaseModel):
    source_id: str = Field(..., min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: bool = True
    use_global_keywords: bool = True
    params: Dict[str, Any] = Field(default_factory=dict)


class SourceConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    enabled: Optional[bool] = None
    use_global_keywords: Optional[bool] = None
    params: Optional[Dict[str, Any]] = None


class SourceConfigResponse(BaseModel):
    id: str
    source_id: str
    name: str
    enabled: bool
    use_global_keywords: bool
    params: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


# --- Keywords ---


class KeywordCreate(BaseModel):
    keywords: List[str] = Field(..., min_length=1)


class KeywordResponse(BaseModel):
    id: str
    text: str
    enabled: bool = True
    created_at: Optional[datetime] = None


class KeywordBulkAction(BaseModel):
    keyword_ids: List[str] = Field(..., min_length=1)
    action: str = Field(..., pattern="^(enable|disable|delete)$")


# --- User Settings ---


class ScheduleConfig(BaseModel):
    type: ScheduleType = ScheduleType.MANUAL
    interval_hours: Optional[int] = Field(None, ge=1, le=168)  # For hourly
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # For weekly (0=Mon)
    hour_of_day: Optional[int] = Field(None, ge=0, le=23)  # For daily/weekly


class UserSettingsUpdate(BaseModel):
    time_window_hours: Optional[int] = Field(None, ge=1, le=168)
    max_trends_per_source: Optional[int] = Field(None, ge=1, le=50)
    schedule: Optional[ScheduleConfig] = None
    reddit_fetch_method: Optional[Literal["rapidapi", "direct"]] = None


class UserSettingsResponse(BaseModel):
    time_window_hours: int = 3
    max_trends_per_source: int = 3
    result_retention_days: int = 15
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    reddit_fetch_method: Literal["rapidapi", "direct"] = "rapidapi"


# --- User Profile & Tiers ---


class TierLimits(BaseModel):
    keywords: int
    reddit_sources: int
    extractions: Dict[str, int]


class UserProfileResponse(BaseModel):
    uid: str
    email: str
    active_tier: str
    tier_limits: TierLimits
    usage: Dict[str, Any]
    settings: UserSettingsResponse


# --- Extraction ---


class ExtractionRequest(BaseModel):
    """Optional overrides for a single extraction run."""

    time_window_hours: Optional[int] = Field(None, ge=1, le=168)
    max_trends_per_source: Optional[int] = Field(None, ge=1, le=50)
    use_keywords: Optional[bool] = None


class ExtractionRunResponse(BaseModel):
    extraction_id: str
    status: Literal["pending", "completed", "failed"] = "completed"
    results_count: int
    results: List["TrendResultResponse"]
    error: Optional[str] = None


class ExtractionResponse(BaseModel):
    id: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    results_count: int
    sources: List[str]
    status: Literal["pending", "completed", "failed"] = "completed"
    error: Optional[str] = None


class ExtractionListResponse(BaseModel):
    extractions: List[ExtractionResponse]
    total: int
    page: int = 1
    page_size: int = 50


# --- Trend Results ---


class TrendResultResponse(BaseModel):
    id: str
    source: str
    source_type: str
    title: str
    url: str
    description: str = ""
    trend_score: float
    ups: int = 0
    comments: int = 0
    created_at: Optional[datetime] = None
    extraction_id: Optional[str] = None


class ResultsListResponse(BaseModel):
    results: List[TrendResultResponse]
    total: int
    page: int = 1
    page_size: int = 50


# --- Admin ---


class AdminConfig(BaseModel):
    source_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "reddit": 1.0,
            "hackernews": 1.0,
            "bluesky": 1.0,
            "indiehackers": 1.0,
        }
    )
    default_retention_days: int = 15


class AdminConfigUpdate(BaseModel):
    source_weights: Optional[Dict[str, float]] = None
    default_retention_days: Optional[int] = Field(None, ge=1, le=365)


# Rebuild forward references
ExtractionRunResponse.model_rebuild()
