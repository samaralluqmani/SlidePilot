from models.deck import Deck, Slide


VALID_LAYOUTS = {
    "title", "content", "bullets", "two_column", "metrics",
    "process", "timeline", "table", "chart", "closing",
}


def validate_deck_layouts(deck: Deck) -> Deck:
    for slide in deck.slides:
        slide.layout = validate_slide_layout(slide)
    return deck


def validate_slide_layout(slide: Slide) -> str:
    layout = slide.layout
    if layout not in VALID_LAYOUTS:
        return choose_fallback_layout(slide)
    if layout == "metrics" and not slide.metrics:
        return choose_fallback_layout(slide)
    if layout == "timeline" and not slide.timeline:
        return choose_fallback_layout(slide)
    if layout == "process" and len(slide.process) < 2:
        return choose_fallback_layout(slide)
    if layout == "two_column" and (not slide.left_items or not slide.right_items):
        return choose_fallback_layout(slide)
    if layout == "table" and (not slide.table or not slide.table.headers or not slide.table.rows):
        return choose_fallback_layout(slide)
    if layout == "chart":
        if not slide.chart or not slide.chart.labels or not slide.chart.values:
            return choose_fallback_layout(slide)
        if len(slide.chart.labels) != len(slide.chart.values):
            return choose_fallback_layout(slide)
    return layout


def choose_fallback_layout(slide: Slide) -> str:
    if slide.left_items and slide.right_items:
        return "two_column"
    if slide.bullets:
        return "bullets"
    if slide.body:
        return "content"
    return "content"
