from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from presentation.components.text import hex_to_rgb
from presentation.theme import Theme


def add_card(
    slide,
    theme: Theme,
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    shadow: bool = True,
    accent_top: bool = False,
):
    """Theme-aware reusable card primitive.

    Business = clean executive card.
    Technology = glass-like dark surface with restrained glow.
    Academic = editorial paper block with rule-based hierarchy.
    """
    if theme.name == "academic":
        card = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(y), Inches(w), Inches(h),
        )
        card.fill.solid()
        card.fill.fore_color.rgb = hex_to_rgb(theme.surface)
        card.line.color.rgb = hex_to_rgb(theme.border_color)
        card.line.transparency = 45

        # Editorial left rule and small gold registration mark.
        rule = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(y), Inches(0.035), Inches(h),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb(theme.primary)
        rule.fill.transparency = 18
        rule.line.fill.background()

        mark = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x + 0.14), Inches(y + 0.14), Inches(0.10), Inches(0.10),
        )
        mark.fill.solid()
        mark.fill.fore_color.rgb = hex_to_rgb(theme.accent)
        mark.fill.transparency = 12
        mark.line.fill.background()

        if accent_top:
            top_rule = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x + 0.34), Inches(y), Inches(max(w - 0.54, 0.10)), Inches(0.020),
            )
            top_rule.fill.solid()
            top_rule.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
            top_rule.line.fill.background()
        return card

    if theme.name == "business" and shadow:
        s = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x + 0.025), Inches(y + 0.035), Inches(w), Inches(h),
        )
        s.fill.solid()
        s.fill.fore_color.rgb = hex_to_rgb(theme.surface_alt)
        s.line.fill.background()

    elif theme.name == "technology" and shadow:
        # Two subtle layers create depth without a heavy neon box.
        s = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x + 0.03), Inches(y + 0.03), Inches(w), Inches(h),
        )
        s.fill.solid()
        s.fill.fore_color.rgb = hex_to_rgb(theme.accent)
        s.fill.transparency = 94
        s.line.fill.background()

        halo = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x - 0.012), Inches(y - 0.012), Inches(w + 0.024), Inches(h + 0.024),
        )
        halo.fill.background()
        halo.line.color.rgb = hex_to_rgb(theme.primary)
        halo.line.transparency = 78
        halo.line.width = Inches(0.010)

    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    card.fill.solid()
    card.fill.fore_color.rgb = hex_to_rgb(theme.surface)

    if theme.name == "technology":
        card.fill.transparency = 8
        card.line.color.rgb = hex_to_rgb(theme.accent)
        card.line.transparency = 68
        card.line.width = Inches(0.010)
    else:
        card.line.color.rgb = hex_to_rgb(theme.border_color)
        card.line.transparency = 60

    if accent_top:
        accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x + 0.20), Inches(y), Inches(max(w - 0.40, 0.1)), Inches(0.030),
        )
        accent.fill.solid()
        accent.fill.fore_color.rgb = hex_to_rgb(
            theme.accent if theme.name == "technology" else theme.primary
        )
        accent.fill.transparency = 4 if theme.name == "technology" else 0
        accent.line.fill.background()

        if theme.name == "technology":
            signal = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x + w - 0.44), Inches(y + 0.14), Inches(0.24), Inches(0.018),
            )
            signal.fill.solid()
            signal.fill.fore_color.rgb = hex_to_rgb(theme.primary)
            signal.fill.transparency = 35
            signal.line.fill.background()

    return card


def add_metric_badge(slide, theme: Theme, *, x: float, y: float, size: float = 0.82):
    if theme.name == "technology":
        glow = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x - 0.04), Inches(y - 0.04), Inches(size + 0.08), Inches(size + 0.08),
        )
        glow.fill.solid()
        glow.fill.fore_color.rgb = hex_to_rgb(theme.accent)
        glow.fill.transparency = 82
        glow.line.fill.background()

        badge_shape = MSO_SHAPE.OVAL
    elif theme.name == "academic":
        badge_shape = MSO_SHAPE.RECTANGLE
    else:
        badge_shape = MSO_SHAPE.OVAL

    badge = slide.shapes.add_shape(
        badge_shape,
        Inches(x), Inches(y), Inches(size), Inches(size),
    )
    badge.fill.solid()

    if theme.name == "business":
        badge.fill.fore_color.rgb = hex_to_rgb(theme.primary)
        badge.line.fill.background()
    elif theme.name == "technology":
        badge.fill.fore_color.rgb = hex_to_rgb(theme.surface_alt)
        badge.fill.transparency = 4
        badge.line.color.rgb = hex_to_rgb(theme.accent)
        badge.line.transparency = 10
        badge.line.width = Inches(0.018)
    else:
        badge.fill.fore_color.rgb = hex_to_rgb(theme.surface)
        badge.line.color.rgb = hex_to_rgb(theme.accent)
        badge.line.width = Inches(0.014)

    return badge
