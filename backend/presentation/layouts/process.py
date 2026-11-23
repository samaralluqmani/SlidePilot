from unicodedata import bidirectional

from pptx.enum.text import MSO_ANCHOR

from models.deck import Slide
from presentation.components.card import add_card
from presentation.components.chrome import add_brand, add_footer, add_heading, apply_background
from presentation.components.text import add_text_box
from presentation.theme import Theme


def _split_step(text: str) -> tuple[str, str]:
    text = " ".join(text.split())
    for separator in (" — ", " – ", " - ", ": "):
        if separator in text:
            title, description = text.split(separator, 1)
            return title, description
    return text, ""


def _is_rtl(text: str) -> bool:
    for character in text:
        direction = bidirectional(character)
        if direction in {"L", "R", "AL"}:
            return direction != "L"
    return False


def _add_step(slide, theme: Theme, step: str, number: int, x: float, y: float,
              width: float, height: float, rtl: bool, compact: bool):
    title, description = _split_step(step)
    accent = theme.accent if theme.name == "technology" else theme.primary
    add_card(slide, theme, x=x, y=y, w=width, h=height, shadow=False, accent_top=True)

    padding = 0.23
    number_width = 0.52
    number_x = x + width - padding - number_width if rtl else x + padding
    title_x = x + padding if rtl else x + padding + number_width
    add_text_box(
        slide, f"{number:02d}", number_x, y + 0.17, number_width, 0.45,
        theme.body_font, 14, accent, True, valign=MSO_ANCHOR.MIDDLE,
    )
    add_text_box(
        slide, title, title_x, y + 0.15, width - 2 * padding - number_width,
        0.56 if description else height - 0.36,
        theme.title_font, 19 if compact else 23, theme.title_color, True,
        valign=MSO_ANCHOR.MIDDLE,
    )
    if description:
        add_text_box(
            slide, description, x + padding, y + 0.74, width - 2 * padding, height - 0.88,
            theme.body_font, 16 if compact else 20, theme.body_color,
        )


def render_process_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme)
    add_brand(slide, theme)
    add_heading(slide, theme, data.title, data.subtitle)

    steps = data.process[:5]
    count = len(steps)
    compact = count > 3
    columns = 2 if count == 4 else min(count, 3)
    rtl = _is_rtl(data.title + " " + " ".join(steps))
    gap = 0.23
    margin = 0.78
    span = 11.77
    if columns:
        width = (span - gap * (columns - 1)) / columns
        height = 1.92 if compact else 3.24
        top = 2.55 if compact else 2.83
        for index, step in enumerate(steps):
            row, column = divmod(index, columns)
            offset = column * (width + gap)
            x = margin + (span - width - offset if rtl else offset)
            _add_step(slide, theme, step, index + 1, x, top + row * (height + gap),
                      width, height, rtl, compact)

    add_footer(slide, theme)
    return slide
