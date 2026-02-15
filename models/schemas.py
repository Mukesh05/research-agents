from pydantic import BaseModel
from typing import Optional, Literal
from enum import Enum


class ResearchResponse(BaseModel):
    """Schema for structured research responses."""
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


class SlideLayout(str, Enum):
    """Available slide layout types for corporate presentations."""
    TITLE = "title-slide"
    EXECUTIVE_SUMMARY = "executive-summary"
    FULL_CHART = "full-chart"
    CHART_INSIGHT = "chart-insight"
    TWO_COLUMN_COMPARE = "two-column-compare"
    DATA_TABLE = "data-table"
    SECTION_DIVIDER = "section-divider"


class ChartSpec(BaseModel):
    """Specification for a chart to be generated."""
    chart_type: Literal["bar", "line", "pie", "doughnut", "area"]
    title: str  # Insight-based title (e.g., "Revenue grew 40% in Q4")
    data: list[float | int]  # Numerical data points
    labels: list[str]  # Labels for data points
    colors: Optional[list[str]] = None  # Custom colors (hex without #)
    show_legend: bool = False
    show_data_labels: bool = True
    layout: SlideLayout = SlideLayout.FULL_CHART
    # Additional insight for chart-insight layout
    insight_text: Optional[str] = None


class TableSpec(BaseModel):
    """Specification for a data table."""
    title: str
    headers: list[str]
    rows: list[list[str | int | float]]
    # Row indices to highlight (0-based)
    highlight_rows: Optional[list[int]] = None
    column_widths: Optional[list[float]] = None  # Column widths in inches


class VisualizationRequest(BaseModel):
    """Request to generate a professional presentation with visualizations."""
    presentation_title: str
    theme: Literal["navy-teal", "navy-gold", "charcoal-blue"] = "navy-teal"
    charts: list[ChartSpec] = []
    tables: list[TableSpec] = []
    executive_summary: Optional[list[str]] = None  # Key findings (numbered)
    section_dividers: Optional[list[str]] = None  # Section titles


class VisualizationResponse(BaseModel):
    """Response after generating visualization presentation."""
    pptx_path: str
    charts_created: int
    tables_created: int
    slide_count: int
