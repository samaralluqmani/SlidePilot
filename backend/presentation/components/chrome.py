from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches

from presentation.components.text import add_text_box, hex_to_rgb
from presentation.theme import Theme


def _rect(slide, x, y, w, h, color: str, transparency: int = 0):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(color)
    if transparency:
        alpha = OxmlElement("a:alpha")
        alpha.set("val", str((100 - max(0, min(transparency, 100))) * 1000))
        shape._element.spPr.solidFill.srgbClr.append(alpha)
    shape.line.fill.background()
    return shape


def _dot(slide, x, y, size, color: str, transparency: int = 0):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x), Inches(y), Inches(size), Inches(size),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(color)
    if transparency:
        alpha = OxmlElement("a:alpha")
        alpha.set("val", str((100 - max(0, min(transparency, 100))) * 1000))
        shape._element.spPr.solidFill.srgbClr.append(alpha)
    shape.line.fill.background()
    return shape


def apply_background(slide, theme: Theme, variant: str = "content"):
    """Apply the theme canvas and layout-specific art direction.

    Variants:
      - cover: title / opening slides
      - data: metrics, charts, tables
      - content: content, comparisons, process, timeline
      - closing: closing / thank-you slides
    """
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(theme.background)

    if theme.name == "business":
        _business_background(slide, theme, variant)
    elif theme.name == "technology":
        _technology_background(slide, theme, variant)
    else:
        _academic_background(slide, theme, variant)


# =========================================================
# BUSINESS — clean consulting / executive system
# =========================================================

def _business_background(slide, theme: Theme, variant: str):
    if variant == "cover":
        _rect(slide, 0, 0, 0.10, 7.5, theme.primary)
        _rect(slide, 10.95, 0, 2.38, 0.10, theme.primary, 20)
        _rect(slide, 11.55, 0.18, 0.78, 0.025, theme.accent, 48)
        return

    if variant == "data":
        _rect(slide, 0, 0.72, 0.10, 1.18, theme.primary)
        _rect(slide, 10.50, 0.38, 1.85, 0.025, theme.primary, 70)
        _rect(slide, 11.48, 0.48, 0.87, 0.025, theme.accent, 76)
        return

    if variant == "closing":
        _rect(slide, 0, 7.39, 13.33, 0.11, theme.primary)
        _rect(slide, 9.85, 7.31, 2.48, 0.025, theme.accent, 35)
        return

    # content
    _rect(slide, 0, 0.58, 0.09, 1.35, theme.primary)
    _rect(slide, 11.25, 0.34, 1.05, 0.025, theme.primary, 65)
    _rect(slide, 11.72, 0.46, 0.58, 0.025, theme.accent, 72)


# =========================================================
# TECHNOLOGY — dark precision / neon system
# =========================================================

def _technology_trace(slide, theme: Theme, y: float, count: int = 4):
    for i in range(count):
        width = 2.15 - i * 0.28
        _rect(
            slide,
            10.08 + i * 0.42,
            y + i * 0.16,
            max(width, 0.5),
            0.018,
            theme.accent if i % 2 else theme.primary,
            65 + i * 5,
        )


def _technology_background(slide, theme: Theme, variant: str):
    if variant == "cover":
        _technology_trace(slide, theme, 0.20, 5)
        _rect(slide, 0.78, 7.12, 2.30, 0.025, theme.primary, 22)
        _rect(slide, 0.78, 7.18, 1.10, 0.025, theme.accent, 15)
        _dot(slide, 12.38, 0.34, 0.12, theme.accent, 10)
        return

    if variant == "data":
        # Data slides use a compact signal rail and a small matrix of luminous nodes.
        _rect(slide, 0, 0.82, 0.055, 1.08, theme.accent, 10)
        for row in range(2):
            for col in range(4):
                _dot(
                    slide,
                    11.22 + col * 0.30,
                    0.35 + row * 0.28,
                    0.055,
                    theme.accent if (row + col) % 2 else theme.primary,
                    48 + (row + col) * 5,
                )
        _rect(slide, 10.92, 0.98, 1.40, 0.018, theme.primary, 78)
        return

    if variant == "closing":
        _rect(slide, 0.78, 6.98, 11.55, 0.022, theme.primary, 48)
        _rect(slide, 0.78, 7.05, 3.05, 0.032, theme.accent, 20)
        _technology_trace(slide, theme, 0.25, 3)
        return

    # content
    _technology_trace(slide, theme, 0.22, 4)
    _dot(slide, 12.36, 0.38, 0.10, theme.accent, 18)
    _rect(slide, 0.10, 6.72, 1.22, 0.018, theme.primary, 82)
    _rect(slide, 0.10, 6.78, 0.62, 0.018, theme.accent, 72)


# =========================================================
# ACADEMIC — editorial / scholarly system
# =========================================================

def _academic_rules(slide, theme: Theme, y: float = 0.42):
    _rect(slide, 0.65, y, 12.0, 0.020, theme.primary, 10)
    _rect(slide, 0.65, y + 0.055, 2.0, 0.030, theme.accent, 5)


def _academic_background(slide, theme: Theme, variant: str):
    if variant == "cover":
        _academic_rules(slide, theme, 0.40)
        _rect(slide, 0.64, 1.48, 0.025, 4.86, theme.primary, 62)
        _rect(slide, 0.56, 1.48, 0.11, 0.11, theme.accent, 5)
        return

    if variant == "data":
        _academic_rules(slide, theme, 0.40)
        _rect(slide, 11.22, 6.90, 1.22, 0.018, theme.primary, 75)
        _rect(slide, 11.76, 6.84, 0.68, 0.018, theme.accent, 60)
        return

    if variant == "closing":
        _academic_rules(slide, theme, 0.40)
        _rect(slide, 0.78, 6.92, 11.55, 0.018, theme.border_color, 5)
        _rect(slide, 0.78, 6.98, 2.20, 0.025, theme.accent, 12)
        return

    # content
    _academic_rules(slide, theme, 0.42)
    _rect(slide, 0.65, 1.17, 0.025, 0.86, theme.primary, 68)
    _rect(slide, 0.58, 1.17, 0.10, 0.10, theme.accent, 12)


# =========================================================
# BRAND / HEADING / FOOTER
# =========================================================

def add_brand(slide, theme: Theme, section: str | None = None):
    """Add only the SlidePilot brand mark.

    Theme/layout labels are intentionally not rendered in exported decks.
    The ``section`` argument is kept for backward compatibility with layouts.
    """
    y = 0.55 if theme.name != "academic" else 0.62
    brand_color = theme.primary if theme.name in {"business", "academic"} else theme.accent

    add_text_box(
        slide, "SLIDEPILOT", 0.78, y, 1.8, 0.28,
        theme.body_font, 9, brand_color, True,
    )

    if theme.name == "technology":
        _rect(slide, 0.78, y + 0.31, 0.52, 0.018, theme.accent, 20)
    elif theme.name == "academic":
        _rect(slide, 0.78, y + 0.31, 0.36, 0.018, theme.accent, 18)

def add_heading(slide, theme: Theme, title: str, subtitle: str | None = None):
    title_y = 1.02 if theme.name != "academic" else 1.05
    add_text_box(
        slide, title, 0.78, title_y, 11.7, 0.78,
        theme.title_font, 25 if len(title) > 55 else theme.typography.title, theme.title_color, True,
    )

    if theme.name == "business":
        _rect(slide, 0.78, 1.71, 0.56, 0.035, theme.primary)
        _rect(slide, 1.38, 1.71, 0.30, 0.035, theme.accent, 45)
    elif theme.name == "technology":
        _rect(slide, 0.78, 1.71, 0.58, 0.045, theme.accent, 5)
        _rect(slide, 1.40, 1.71, 0.26, 0.045, theme.primary, 10)
    else:
        _rect(slide, 0.78, 1.71, 2.30, 0.022, theme.border_color)
        _rect(slide, 0.78, 1.71, 0.72, 0.028, theme.accent, 8)

    if subtitle:
        add_text_box(
            slide, subtitle, 0.78, 1.80, 11.7, 0.36,
            theme.body_font, 12, theme.muted_color,
        )


def add_footer(slide, theme: Theme, text: str | None = None):
    """Render decorative footer chrome only.

    Layout/type labels are intentionally hidden from exported presentations.
    ``text`` remains accepted so existing layout calls do not need to change.
    """
    _rect(slide, 0.78, 6.93, 11.77, 0.014, theme.border_color)
    _rect(slide, 0.78, 6.93, 0.55, 0.026, theme.accent)
