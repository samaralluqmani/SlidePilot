from pptx.enum.text import PP_ALIGN

from models.deck import Slide
from presentation.components.card import add_card, add_metric_badge
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.icons import add_metric_icon
from presentation.components.text import add_text_box
from presentation.theme import Theme


def _metric_font_size(count: int, value: str) -> int:
    base = 30 if count <= 2 else 25 if count == 3 else 22
    if len(value) > 10:
        return max(base - 4, 18)
    return base


def _label_font_size(count: int) -> int:
    return 11 if count <= 2 else 10


def render_metrics_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="data")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    metrics = data.metrics[:4]
    if not metrics:
        add_footer(slide, theme, "KEY METRICS")
        return slide

    count = len(metrics)
    if count == 1:
        total_w, gap, start_x = 5.7, 0, 3.82
    elif count == 2:
        total_w, gap, start_x = 10.25, 0.46, 1.52
    elif count == 3:
        total_w, gap, start_x = 11.25, 0.30, 1.02
    else:
        total_w, gap, start_x = 11.55, 0.22, 0.86

    card_w = (total_w - gap * (count - 1)) / count
    card_y, card_h = 2.62, 2.60

    for index, metric in enumerate(metrics):
        x = start_x + index * (card_w + gap)
        add_card(slide, theme, x=x, y=card_y, w=card_w, h=card_h, shadow=True, accent_top=True)

        badge_size = 0.82 if count <= 3 else 0.70
        badge_x = x + (0.42 if count <= 3 else 0.28)
        badge_y = card_y + 0.86
        add_metric_badge(slide, theme, x=badge_x, y=badge_y, size=badge_size)
        add_metric_icon(slide, theme, x=badge_x, y=badge_y, size=badge_size, variant=index)

        content_x = x + (1.55 if count <= 3 else 1.15)
        content_w = card_w - (1.83 if count <= 3 else 1.40)
        value_color = theme.accent if theme.name == "technology" else theme.primary

        add_text_box(
            slide, metric.value, content_x, card_y + 0.62, content_w, 0.66,
            theme.title_font, _metric_font_size(count, metric.value), value_color, True, PP_ALIGN.LEFT,
        )
        add_text_box(
            slide, metric.label, content_x, card_y + 1.34, content_w, 0.78,
            theme.body_font, _label_font_size(count), theme.body_color, False, PP_ALIGN.LEFT,
        )

    add_footer(slide, theme, "KEY METRICS")
    return slide
