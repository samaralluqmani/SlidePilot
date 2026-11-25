from io import BytesIO
from unicodedata import bidirectional

from PIL import Image, UnidentifiedImageError
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

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


def _source_aspect(image_bytes: bytes) -> float | None:
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            return image.width / image.height
    except (UnidentifiedImageError, OSError):
        return None


def _add_source_image(slide, image_bytes: bytes, aspect: float, x: float, y: float, width: float, height: float):
    picture_width = min(width, height * aspect)
    picture_height = picture_width / aspect
    slide.shapes.add_picture(
        BytesIO(image_bytes),
        Inches(x + (width - picture_width) / 2),
        Inches(y + (height - picture_height) / 2),
        Inches(picture_width),
        Inches(picture_height),
    )


def _add_evidence_caption(
    slide, data: Slide, theme: Theme, label: str | None,
    x: float, y: float, width: float, centered: bool = False,
):
    alignment = PP_ALIGN.CENTER if centered else None
    if data.visual_caption:
        add_text_box(
            slide, data.visual_caption, x, y, width, 0.34,
            theme.body_font, 12, theme.body_color, align=alignment,
        )
        y += 0.34
    if label:
        add_text_box(
            slide, label, x, y, width, 0.30,
            theme.body_font, 11, theme.muted_color, align=alignment,
        )


def render_evidence_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme)
    add_brand(slide, theme)
    add_heading(slide, theme, data.title, data.subtitle if data.body else None)

    takeaway = data.body or data.subtitle
    label = data.source_visual_label
    source_aspect = _source_aspect(image_bytes) if image_bytes and label else None
    if label and source_aspect is None:
        image_bytes = None

    story_y, story_h, alignment = 2.58, 3.63, None
    if source_aspect and source_aspect >= 1.8 and len(takeaway or "") <= 140 and not data.bullets:
        _add_source_image(slide, image_bytes, source_aspect, 0.78, 2.23, 11.77, 3.01)
        _add_evidence_caption(slide, data, theme, label, 0.78, 5.28, 11.77, centered=True)
        story_x, story_w = 1.18, 10.97
        story_y, story_h, alignment = 5.99, 0.88, PP_ALIGN.CENTER
    elif image_bytes:
        rtl = _reads_right_to_left(data.title)
        image_w = 5.75 if source_aspect and source_aspect < 1.15 else 7.25
        story_w = 11.77 - 0.42 - image_w
        image_x = 0.78 + story_w + 0.42 if rtl else 0.78
        story_x = 0.78 if rtl else 0.78 + image_w + 0.42
        if source_aspect:
            _add_source_image(slide, image_bytes, source_aspect, image_x, 2.28, image_w, 3.78)
            _add_evidence_caption(slide, data, theme, label, image_x, 6.11, image_w, centered=True)
        else:
            add_visual_panel(slide, theme, image_bytes, image_x, 2.28, image_w, 4.08)
            _add_evidence_caption(slide, data, theme, None, image_x, 6.49, image_w)
    else:
        story_x, story_w = 1.18, 10.97
        add_card(slide, theme, x=0.78, y=2.50, w=11.77, h=3.7, shadow=False, accent_top=True)

    if takeaway:
        add_text_box(
            slide, takeaway, story_x, story_y, story_w, story_h,
            theme.body_font, 19 if image_bytes and (len(takeaway) > 140 or alignment is not None) else 24,
            theme.body_color, align=alignment, valign=MSO_ANCHOR.MIDDLE,
        )
    elif data.bullets:
        accent = theme.accent if theme.name == "technology" else theme.primary
        add_bullet_list(
            slide, data.bullets, story_x, 2.67, story_w, 3.48,
            theme.body_font, 17 if image_bytes else 20, theme.body_color, accent, 8,
        )

    add_footer(slide, theme)
    return slide
