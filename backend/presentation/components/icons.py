from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from presentation.components.text import hex_to_rgb
from presentation.theme import Theme, contrasting_text


def _icon_color(theme: Theme) -> str:
    if theme.name == "business":
        return contrasting_text(theme.primary)
    if theme.name == "technology":
        return theme.accent
    return theme.primary


def add_metric_icon(slide, theme: Theme, *, x: float, y: float, size: float, variant: int = 0):
    """Draw simple editable PowerPoint glyphs; no external icon assets required."""
    color = _icon_color(theme)
    left = x + size * 0.23
    top = y + size * 0.25
    iw = size * 0.54
    ih = size * 0.50

    if variant % 4 == 0:  # growth bars
        heights = (0.23, 0.38, 0.56)
        for i, ratio in enumerate(heights):
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(left + i * iw * 0.31), Inches(top + ih * (1-ratio)), Inches(iw * 0.18), Inches(ih * ratio),
            )
            bar.fill.solid(); bar.fill.fore_color.rgb = hex_to_rgb(color); bar.line.fill.background()
    elif variant % 4 == 1:  # people / acquisition
        for dx, dy, scale in ((0.10, 0.00, 0.23), (0.42, 0.06, 0.20), (0.70, 0.00, 0.23)):
            head = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left + iw*dx), Inches(top + ih*dy), Inches(iw*scale), Inches(iw*scale))
            head.fill.solid(); head.fill.fore_color.rgb = hex_to_rgb(color); head.line.fill.background()
        base = slide.shapes.add_shape(MSO_SHAPE.ARC, Inches(left + iw*0.10), Inches(top + ih*0.34), Inches(iw*0.78), Inches(ih*0.48))
        base.fill.background(); base.line.color.rgb = hex_to_rgb(color); base.line.width = Inches(0.025)
    elif variant % 4 == 2:  # target
        for shrink in (0.0, 0.16, 0.31):
            ring = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(left + iw*shrink), Inches(top + ih*shrink), Inches(iw*(1-2*shrink)), Inches(ih*(1-2*shrink)),
            )
            ring.fill.background(); ring.line.color.rgb = hex_to_rgb(color); ring.line.width = Inches(0.018)
    else:  # shield-like marker
        shield = slide.shapes.add_shape(MSO_SHAPE.PENTAGON, Inches(left + iw*0.10), Inches(top), Inches(iw*0.80), Inches(ih))
        shield.fill.background(); shield.line.color.rgb = hex_to_rgb(color); shield.line.width = Inches(0.025)
    return None
