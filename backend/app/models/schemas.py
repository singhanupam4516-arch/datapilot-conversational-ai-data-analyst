"""Pydantic request/response models shared across routers."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---- Phase 1: Ingestion ----------------------------------------------------

class ColumnInfo(BaseModel):
    name: str
    dtype: str


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    row_count: int
    column_count: int
    columns: list[ColumnInfo]
    uploaded_at: datetime


# ---- Phase 2: EDA -----------------------------------------------------------

class NumericStats(BaseModel):
    mean: float
    median: float
    std: float
    min: float
    max: float
    count: int


class CategoricalStats(BaseModel):
    unique_count: int
    top_values: dict[str, int]


class ChartImage(BaseModel):
    column: str
    chart_type: str
    image_base64: str


class EDAResponse(BaseModel):
    numeric_summary: dict[str, NumericStats]
    categorical_summary: dict[str, CategoricalStats]
    distribution_charts: list[ChartImage]
    correlation_heatmap: str | None = None


# ---- Phase 4: Conversational loop -------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    generated_code: str
    result: Any = None
    chart_base64: str | None = None
    timestamp: datetime


class ChatHistoryItem(BaseModel):
    question: str
    answer: str
    generated_code: str
    result: Any = None
    chart_base64: str | None = None
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryItem]
