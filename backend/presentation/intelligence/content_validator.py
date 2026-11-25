import re
import unicodedata

from models.deck import Deck, Slide


MAX_BULLETS = 5
MAX_BULLET_LENGTH = 100
MAX_BODY_LENGTH = 330
MAX_COLUMN_ITEMS = 5
MAX_COLUMN_ITEM_LENGTH = 90
MAX_METRICS = 4
MAX_METRIC_VALUE_LENGTH = 13
MAX_METRIC_LABEL_LENGTH = 50
MAX_PROCESS_STEPS = 5
MAX_PROCESS_TEXT_LENGTH = 110
MAX_TIMELINE_ITEMS = 5
MAX_TIMELINE_DESCRIPTION_LENGTH = 135
MAX_TABLE_ROWS = 7
MAX_TABLE_COLUMNS = 5
MAX_TABLE_CELL_LENGTH = 110
MAX_CHART_POINTS = 8


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def shorten_text(text: str, max_length: int) -> str:
    text = normalize_text(text)
    if len(text) <= max_length:
        return text
    # Word-safe shortening for narrative fields where a hard cap is still useful.
    clipped = text[:max_length].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return (clipped or text[:max_length]).rstrip() + "…"


def preserve_text(text: str, max_length: int) -> str:
    """Keep structured-data copy intact unless it is pathologically long.

    Process, timeline, and table renderers can now fit and wrap text dynamically,
    so we avoid adding visible ellipses during validation.
    """
    text = normalize_text(text)
    if len(text) <= max_length:
        return text
    clipped = text[:max_length].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return clipped or text[:max_length]


def validate_deck_content(deck: Deck) -> Deck:
    deck.title = shorten_text(deck.title, 80)
    if deck.subtitle:
        deck.subtitle = shorten_text(deck.subtitle, 120)

    for slide in deck.slides:
        normalize_slide(slide)
    _merge_repeated_closing(deck)
    return deck


def _comparison_key(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"[^\W_]+", text))


def _merge_repeated_closing(deck: Deck) -> None:
    if len(deck.slides) <= 3:
        return
    previous, closing = deck.slides[-2:]
    if previous.layout not in {"content", "bullets", "takeaway"} or closing.layout != "closing":
        return
    if previous.source_visual_id or previous.visual_prompt:
        return

    closing_text = closing.body or closing.subtitle or next(iter(closing.bullets), "")
    closing_key = _comparison_key(closing_text)
    details = [
        key for value in (previous.subtitle, previous.body, *previous.bullets)
        if value and (key := _comparison_key(value))
    ]
    repeated = {
        separator.join(details) for separator in (" ", " and ", " و ", " و")
    } if details else set()
    if closing_key in repeated:
        del deck.slides[-2]


def normalize_slide(slide: Slide) -> None:
    slide.title = shorten_text(slide.title, 70)
    if slide.subtitle:
        slide.subtitle = shorten_text(slide.subtitle, 110)
    if slide.body:
        slide.body = shorten_text(slide.body, MAX_BODY_LENGTH)

    slide.bullets = [shorten_text(x, MAX_BULLET_LENGTH) for x in slide.bullets[:MAX_BULLETS]]
    slide.left_items = [shorten_text(x, MAX_COLUMN_ITEM_LENGTH) for x in slide.left_items[:MAX_COLUMN_ITEMS]]
    slide.right_items = [shorten_text(x, MAX_COLUMN_ITEM_LENGTH) for x in slide.right_items[:MAX_COLUMN_ITEMS]]

    # Structured visuals are rendered with adaptive sizing; preserve the actual wording.
    slide.process = [preserve_text(x, MAX_PROCESS_TEXT_LENGTH) for x in slide.process[:MAX_PROCESS_STEPS]]

    slide.metrics = slide.metrics[:MAX_METRICS]
    for metric in slide.metrics:
        metric.value = shorten_text(metric.value, MAX_METRIC_VALUE_LENGTH)
        metric.label = shorten_text(metric.label, MAX_METRIC_LABEL_LENGTH)

    slide.timeline = slide.timeline[:MAX_TIMELINE_ITEMS]
    for event in slide.timeline:
        event.label = preserve_text(event.label, 28)
        event.description = preserve_text(event.description, MAX_TIMELINE_DESCRIPTION_LENGTH)

    if slide.table:
        slide.table.headers = [preserve_text(x, 36) for x in slide.table.headers[:MAX_TABLE_COLUMNS]]
        slide.table.rows = [
            [preserve_text(str(cell), MAX_TABLE_CELL_LENGTH) for cell in row[:MAX_TABLE_COLUMNS]]
            for row in slide.table.rows[:MAX_TABLE_ROWS]
        ]

    if slide.chart:
        count = min(len(slide.chart.labels), len(slide.chart.values), MAX_CHART_POINTS)
        slide.chart.labels = [shorten_text(x, 24) for x in slide.chart.labels[:count]]
        slide.chart.values = slide.chart.values[:count]
        if slide.chart.value_label:
            slide.chart.value_label = shorten_text(slide.chart.value_label, 60) or None

    if slide.visual_prompt:
        slide.visual_prompt = shorten_text(slide.visual_prompt, 380)
    if slide.visual_caption:
        slide.visual_caption = shorten_text(slide.visual_caption, 80)
