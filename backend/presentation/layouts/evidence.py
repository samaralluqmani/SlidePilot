from unicodedata import bidirectional

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from models.deck import Slide
from presentation.components.card import add_card
from presentation.components.chrome import add_brand, add_footer, add_heading, apply_background
from presentation.components.text import add_bullet_list, add_text_box
from presentation.components.visual import add_visual_panel
from presentation.layouts.content import render_content_slide
from presentation.theme import Theme


def _reads_right_to_left(text: str) -> bool:
    for character in text:
        direction = bidirectional(character)
        if direction in {"L", "R", "AL"}:
            return direction in {"R", "AL"}
    return False


def render_metric_story_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    if not data.metrics:
        return render_content_slide(prs, data, theme)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="data")
    add_brand(slide, theme)
    add_heading(slide, theme, data.title, data.subtitle if data.body else None)

    takeaway = data.body or data.subtitle
    metric = data.metrics[0]
    rtl = _reads_right_to_left(data.title)
    metric_x, story_x = (7.98, 0.78) if rtl else (0.78, 5.85)
    accent = theme.accent if theme.name == "technology" else theme.primary

    add_card(slide, theme, x=metric_x, y=2.5, w=4.57, h=3.7, shadow=False, accent_top=True)
    add_text_box(
        slide, metric.value, metric_x + 0.22, 2.87, 4.13, 1.5,
        theme.title_font, 38 if len(metric.value) > 8 else 54, accent, True,
        align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE,
    )
    add_text_box(
        slide, metric.label, metric_x + 0.35, 4.48, 3.87, 1.25,
        theme.body_font, 20, theme.body_color,
        align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE,
    )

    if takeaway:
        add_text_box(
            slide, takeaway, story_x, 2.64, 6.7, 3.42,
            theme.body_font, 21 if len(takeaway) > 150 else 26, theme.body_color,
            valign=MSO_ANCHOR.MIDDLE,
        )
    elif data.bullets:
        add_bullet_list(
            slide, data.bullets, story_x, 2.74, 6.7, 3.42,
            theme.body_font, 18, theme.body_color, accent, 10,
        )

    add_footer(slide, theme)
    return slide


def render_evidence_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme)
    add_brand(slide, theme)
    add_heading(slide, theme, data.title, data.subtitle if data.body else None)

    takeaway = data.body or data.subtitle
    if image_bytes:
        rtl = _reads_right_to_left(data.title)
        image_x, story_x = (5.30, 0.78) if rtl else (0.78, 8.45)
        story_w = 4.1
        add_visual_panel(slide, theme, image_bytes, image_x, 2.28, 7.25, 4.08)
        if data.visual_caption:
            add_text_box(
                slide, data.visual_caption, image_x, 6.49, 7.25, 0.36,
                theme.body_font, 12, theme.muted_color,
            )
    else:
        story_x, story_w = 1.18, 10.97
        add_card(slide, theme, x=0.78, y=2.50, w=11.77, h=3.7, shadow=False, accent_top=True)

    if takeaway:
        add_text_box(
            slide, takeaway, story_x, 2.58, story_w, 3.63,
            theme.body_font, 19 if image_bytes and len(takeaway) > 140 else 24,
            theme.body_color, valign=MSO_ANCHOR.MIDDLE,
        )
    elif data.bullets:
        accent = theme.accent if theme.name == "technology" else theme.primary
        add_bullet_list(
            slide, data.bullets, story_x, 2.67, story_w, 3.48,
            theme.body_font, 17 if image_bytes else 20, theme.body_color, accent, 8,
        )

    add_footer(slide, theme)
    return slide
