from typing import Literal

from pydantic import BaseModel, Field


ThemeName = Literal["business", "technology", "academic", "culinary", "travel", "nature", "culture", "editorial"]
SlideLayout = Literal[
    "title",
    "takeaway",
    "content",
    "bullets",
    "two_column",
    "metrics",
    "metric_story",
    "evidence",
    "process",
    "timeline",
    "table",
    "chart",
    "closing",
]
VisualStyle = Literal["none", "abstract", "illustration", "photo", "diagram"]


class MetricItem(BaseModel):
    label: str
    value: str


class TimelineItem(BaseModel):
    label: str
    description: str


class TableData(BaseModel):
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class ChartData(BaseModel):
    chart_type: Literal["bar", "line", "pie"]
    labels: list[str] = Field(default_factory=list)
    values: list[float] = Field(default_factory=list)
    value_label: str | None = None


class Slide(BaseModel):
    layout: SlideLayout
    title: str
    subtitle: str | None = None
    body: str | None = None
    bullets: list[str] = Field(default_factory=list)

    left_title: str | None = None
    left_items: list[str] = Field(default_factory=list)
    right_title: str | None = None
    right_items: list[str] = Field(default_factory=list)

    metrics: list[MetricItem] = Field(default_factory=list)
    process: list[str] = Field(default_factory=list)
    timeline: list[TimelineItem] = Field(default_factory=list)
    table: TableData | None = None
    chart: ChartData | None = None

    # Visual intelligence. The presentation can still render when no image is generated.
    visual_style: VisualStyle = "none"
    visual_prompt: str | None = None
    visual_caption: str | None = None
    source_visual_id: str | None = None
    source_visual_label: str | None = None


class ArtDirection(BaseModel):
    primary: str
    accent: str
    canvas: Literal["light", "dark"]
    imagery: str


class Deck(BaseModel):
    title: str
    subtitle: str | None = None
    author: str | None = None
    theme: ThemeName
    slides: list[Slide]
    art_direction: ArtDirection | None = None
