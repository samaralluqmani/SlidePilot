from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

from models.deck import Slide
from presentation.components.card import add_card
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.text import add_text_box, hex_to_rgb
from presentation.theme import Theme, contrasting_text


def _timeline_font(text: str, count: int) -> float:
    if len(text) > 110:
        return 7.4
    if len(text) > 82:
        return 8.0
    if len(text) > 58 or count >= 5:
        return 8.5
    return 9.2


def render_timeline_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="content")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    events = data.timeline[:5]
    if not events:
        add_footer(slide, theme, "TIMELINE")
        return slide

    count = len(events)

    if theme.name == "business":
        left, right, node_y = 1.20, 12.00, 3.48
        step = (right - left) / max(count - 1, 1)
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(left), Inches(node_y + 0.20), Inches(right - left), Inches(0.035),
        )
        line.fill.solid()
        line.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
        line.line.fill.background()

        for index, event in enumerate(events):
            cx = left + index * step
            node = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(cx - 0.22), Inches(node_y), Inches(0.44), Inches(0.44),
            )
            node.fill.solid()
            node.fill.fore_color.rgb = hex_to_rgb(theme.primary)
            node.line.fill.background()
            add_text_box(
                slide, f"{index + 1:02d}", cx - 0.18, node_y + 0.09, 0.36, 0.18,
                theme.body_font, 7, contrasting_text(theme.primary), True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
            )
            add_text_box(
                slide, event.label, cx - 0.80, 2.70, 1.60, 0.42,
                theme.body_font, 10, theme.primary, True, PP_ALIGN.CENTER,
            )

            card_w = 2.05 if count >= 5 else 2.48 if count == 4 else 2.75
            card_x = max(0.68, min(cx - card_w / 2, 12.65 - card_w))
            add_card(slide, theme, x=card_x, y=4.12, w=card_w, h=1.45, shadow=False)

            # Small stem visually connects each milestone with its card.
            stem = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(cx - 0.01), Inches(node_y + 0.43), Inches(0.02), Inches(0.24),
            )
            stem.fill.solid()
            stem.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
            stem.line.fill.background()

            add_text_box(
                slide, event.description, card_x + 0.16, 4.30, card_w - 0.32, 1.02,
                theme.body_font, _timeline_font(event.description, count),
                theme.body_color, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
            )

    elif theme.name == "technology":
        x_line = 2.18
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x_line), Inches(2.55), Inches(0.035), Inches(3.55),
        )
        line.fill.solid()
        line.fill.fore_color.rgb = hex_to_rgb(theme.accent)
        line.fill.transparency = 20
        line.line.fill.background()
        gap = 3.35 / max(count - 1, 1)

        for index, event in enumerate(events):
            y = 2.48 + index * gap
            glow = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(1.92), Inches(y - 0.04), Inches(0.55), Inches(0.55),
            )
            glow.fill.solid()
            glow.fill.fore_color.rgb = hex_to_rgb(theme.accent)
            glow.fill.transparency = 72
            glow.line.fill.background()

            node = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(2.02), Inches(y + 0.06), Inches(0.35), Inches(0.35),
            )
            node.fill.solid()
            node.fill.fore_color.rgb = hex_to_rgb(theme.accent)
            node.line.fill.background()

            add_text_box(
                slide, event.label, 0.72, y + 0.02, 1.0, 0.32,
                theme.body_font, 10, theme.accent, True, PP_ALIGN.RIGHT,
            )
            add_text_box(
                slide, event.description, 2.75, y - 0.08, 8.95, 0.62,
                theme.body_font, 11.5 if len(event.description) < 90 else 10.3,
                theme.body_color, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE,
            )

    else:
        # Academic: restrained vertical research chronology.
        top = 2.58
        gap = 0.74 if count >= 5 else 0.86
        line_x = 2.66
        guide = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(line_x), Inches(top + 0.15), Inches(0.018), Inches(gap * (count - 1)),
        )
        guide.fill.solid()
        guide.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
        guide.line.fill.background()

        for index, event in enumerate(events):
            y = top + index * gap
            add_text_box(
                slide, event.label, 0.82, y, 1.45, 0.34,
                theme.title_font, 10, theme.primary, True, PP_ALIGN.RIGHT,
            )

            node = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(line_x - 0.09), Inches(y + 0.08), Inches(0.20), Inches(0.20),
            )
            node.fill.solid()
            node.fill.fore_color.rgb = hex_to_rgb(theme.accent)
            node.line.fill.background()

            add_text_box(
                slide, event.description, 3.10, y - 0.05, 8.65, 0.48,
                theme.body_font, 10.8 if len(event.description) < 100 else 9.8,
                theme.body_color, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE,
            )

    add_footer(slide, theme, "TIMELINE")
    return slide
