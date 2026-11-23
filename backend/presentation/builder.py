from io import BytesIO

from pptx import Presentation
from pptx.util import Inches

from models.deck import Deck, Slide
from presentation.layouts.chart import render_chart_slide
from presentation.layouts.closing import render_closing_slide
from presentation.layouts.content import render_content_slide
from presentation.layouts.evidence import render_evidence_slide, render_metric_story_slide
from presentation.layouts.metrics import render_metrics_slide
from presentation.layouts.process import render_process_slide
from presentation.layouts.table import render_table_slide
from presentation.layouts.takeaway import render_takeaway_slide
from presentation.layouts.timeline import render_timeline_slide
from presentation.layouts.title import render_title_slide
from presentation.layouts.two_column import render_two_column_slide
from presentation.theme import Theme, get_deck_theme


RENDERERS = {
    "title": render_title_slide,
    "takeaway": render_takeaway_slide,
    "content": render_content_slide,
    "bullets": render_content_slide,
    "two_column": render_two_column_slide,
    "metrics": render_metrics_slide,
    "metric_story": render_metric_story_slide,
    "evidence": render_evidence_slide,
    "process": render_process_slide,
    "timeline": render_timeline_slide,
    "table": render_table_slide,
    "chart": render_chart_slide,
    "closing": render_closing_slide,
}


def build_presentation(deck: Deck, visuals: dict[int, bytes] | None = None) -> BytesIO:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    theme = get_deck_theme(deck.theme, deck.art_direction)
    visuals = visuals or {}

    for index, slide_data in enumerate(deck.slides):
        add_slide(prs, slide_data, theme, visuals.get(index))

    output = BytesIO()
    prs.save(output)
    output.seek(0)
    return output


def add_slide(prs: Presentation, slide_data: Slide, theme: Theme, image_bytes: bytes | None = None):
    renderer = RENDERERS.get(slide_data.layout, render_content_slide)
    return renderer(prs, slide_data, theme, image_bytes)
