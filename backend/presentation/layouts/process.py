from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

from models.deck import Slide
from presentation.components.card import add_card
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.icons import add_metric_icon
from presentation.components.text import add_text_box, hex_to_rgb
from presentation.theme import Theme


def _split_step(text: str) -> tuple[str, str]:
    text = " ".join(text.split())
    for separator in (" — ", " – ", " - ", ": "):
        if separator in text:
            title, description = text.split(separator, 1)
            return title.strip(), description.strip()

    words = text.split()
    if len(words) <= 5:
        return text, ""
    return " ".join(words[:3]), " ".join(words[3:])


def _description_font(text: str, count: int) -> float:
    if len(text) > 85:
        return 6.8
    if len(text) > 62:
        return 7.2
    if len(text) > 42 or count >= 5:
        return 7.7
    return 8.3


def _render_horizontal_process(slide, steps: list[str], theme: Theme):
    count = len(steps)
    left, right = 1.12, 12.02
    step_gap = (right - left) / max(count - 1, 1)
    y_node = 3.25

    connector = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(y_node + 0.25), Inches(right - left), Inches(0.035),
    )
    connector.fill.solid()
    connector.fill.fore_color.rgb = hex_to_rgb(
        theme.accent if theme.name == "technology" else theme.border_color
    )
    connector.fill.transparency = 20 if theme.name == "technology" else 0
    connector.line.fill.background()

    for index, step in enumerate(steps):
        title, description = _split_step(step)
        cx = left + index * step_gap

        if theme.name == "technology":
            halo = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(cx - 0.34), Inches(y_node - 0.09), Inches(0.68), Inches(0.68),
            )
            halo.fill.solid()
            halo.fill.fore_color.rgb = hex_to_rgb(theme.accent)
            halo.fill.transparency = 78
            halo.line.fill.background()

        node = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(cx - 0.27), Inches(y_node), Inches(0.54), Inches(0.54),
        )
        node.fill.solid()
        if theme.name == "business":
            node.fill.fore_color.rgb = hex_to_rgb(theme.primary)
            node.line.fill.background()
            number_color = "FFFFFF"
        else:
            node.fill.fore_color.rgb = hex_to_rgb(theme.surface)
            node.line.color.rgb = hex_to_rgb(theme.accent)
            number_color = theme.accent

        add_text_box(
            slide, f"{index + 1:02d}", cx - 0.20, y_node + 0.12, 0.40, 0.20,
            theme.body_font, 8, number_color, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
        )

        card_w = 2.02 if count >= 5 else 2.34
        card_x = max(0.68, min(cx - card_w / 2, 12.65 - card_w))
        card_y = 4.06
        card_h = 1.62
        add_card(
            slide, theme, x=card_x, y=card_y, w=card_w, h=card_h,
            shadow=theme.name == "business",
        )

        icon_size = 0.46
        icon_x = card_x + 0.16
        icon_y = card_y + 0.18
        badge = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(icon_x), Inches(icon_y), Inches(icon_size), Inches(icon_size),
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = hex_to_rgb(
            theme.primary if theme.name == "business" else theme.surface_alt
        )
        badge.line.fill.background()
        add_metric_icon(slide, theme, x=icon_x, y=icon_y, size=icon_size, variant=index)

        add_text_box(
            slide, title, card_x + 0.72, card_y + 0.17, card_w - 0.86, 0.34,
            theme.body_font, 8.8 if count >= 5 else 9.5,
            theme.title_color, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE,
        )
        if description:
            add_text_box(
                slide, description, card_x + 0.16, card_y + 0.70, card_w - 0.32, 0.72,
                theme.body_font, _description_font(description, count), theme.body_color,
                False, PP_ALIGN.LEFT,
            )



def _render_business_process(slide, steps: list[str], theme: Theme):
    count = len(steps)
    left, right = 1.10, 12.02
    step_gap = (right - left) / max(count - 1, 1)
    y_node = 3.18

    connector = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(y_node + 0.25), Inches(right - left), Inches(0.035),
    )
    connector.fill.solid()
    connector.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
    connector.line.fill.background()

    # One shared process surface gives Business slides a cleaner consulting-style rhythm.
    panel_x, panel_y, panel_w, panel_h = 0.72, 4.02, 11.90, 1.70
    add_card(slide, theme, x=panel_x, y=panel_y, w=panel_w, h=panel_h, shadow=True)

    col_w = panel_w / count
    for index, step in enumerate(steps):
        title, description = _split_step(step)
        cx = left + index * step_gap

        node = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(cx - 0.27), Inches(y_node), Inches(0.54), Inches(0.54),
        )
        node.fill.solid()
        node.fill.fore_color.rgb = hex_to_rgb(theme.primary)
        node.line.fill.background()
        add_text_box(
            slide, f"{index + 1:02d}", cx - 0.20, y_node + 0.12, 0.40, 0.20,
            theme.body_font, 8, "FFFFFF", True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
        )

        col_x = panel_x + index * col_w
        icon_size = 0.52
        icon_x = col_x + col_w / 2 - icon_size / 2
        icon_y = panel_y + 0.16
        badge = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(icon_x), Inches(icon_y), Inches(icon_size), Inches(icon_size),
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = hex_to_rgb(theme.primary)
        badge.line.fill.background()
        add_metric_icon(slide, theme, x=icon_x, y=icon_y, size=icon_size, variant=index)

        add_text_box(
            slide, title, col_x + 0.10, panel_y + 0.73, col_w - 0.20, 0.28,
            theme.body_font, 8.8, theme.title_color, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
        )
        if description:
            add_text_box(
                slide, description, col_x + 0.12, panel_y + 1.04, col_w - 0.24, 0.48,
                theme.body_font, 7.2 if len(description) > 55 else 7.7,
                theme.body_color, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
            )

        if index < count - 1:
            divider = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(col_x + col_w - 0.01), Inches(panel_y + 0.18), Inches(0.015), Inches(1.30),
            )
            divider.fill.solid()
            divider.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
            divider.fill.transparency = 35
            divider.line.fill.background()


def _render_academic_process(slide, steps: list[str], theme: Theme):
    """Editorial process treatment: readable numbered rows instead of tiny cards."""
    top = 2.62
    gap = 0.76 if len(steps) >= 5 else 0.88
    number_x = 0.88
    title_x = 1.70
    description_x = 3.52

    # A restrained vertical guide reinforces sequence without making it look corporate.
    guide = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1.17), Inches(top + 0.16), Inches(0.018), Inches(gap * (len(steps) - 1)),
    )
    guide.fill.solid()
    guide.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
    guide.line.fill.background()

    for index, step in enumerate(steps):
        title, description = _split_step(step)
        y = top + index * gap

        node = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(number_x), Inches(y), Inches(0.58), Inches(0.58),
        )
        node.fill.solid()
        node.fill.fore_color.rgb = hex_to_rgb(theme.background)
        node.line.color.rgb = hex_to_rgb(theme.accent)
        node.line.width = Inches(0.018)

        add_text_box(
            slide, f"{index + 1:02d}", number_x + 0.08, y + 0.17, 0.42, 0.18,
            theme.body_font, 8, theme.primary, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE,
        )

        add_text_box(
            slide, title, title_x, y + 0.04, 1.55, 0.48,
            theme.title_font, 10.5, theme.primary, True, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE,
        )
        add_text_box(
            slide, description, description_x, y + 0.02, 8.15, 0.52,
            theme.body_font, 10.2 if len(description) < 80 else 9.3,
            theme.body_color, False, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE,
        )

        if index < len(steps) - 1:
            rule = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(1.70), Inches(y + 0.66), Inches(9.95), Inches(0.015),
            )
            rule.fill.solid()
            rule.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
            rule.fill.transparency = 28
            rule.line.fill.background()


def render_process_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="content")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    steps = data.process[:5]
    if not steps:
        add_footer(slide, theme, "PROCESS / WORKFLOW")
        return slide

    if theme.name == "academic":
        _render_academic_process(slide, steps, theme)
    elif theme.name == "business":
        _render_business_process(slide, steps, theme)
    else:
        _render_horizontal_process(slide, steps, theme)

    add_footer(slide, theme, "PROCESS / WORKFLOW")
    return slide
