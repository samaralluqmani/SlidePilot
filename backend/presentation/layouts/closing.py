from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

from models.deck import Slide
from presentation.components.chrome import add_brand, add_footer, apply_background
from presentation.components.text import add_text_box, hex_to_rgb
from presentation.theme import Theme


def _add_panel(slide, theme: Theme):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE if theme.name == "academic" else MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.95), Inches(1.27), Inches(11.43), Inches(5.28),
    )
    shape.shadow.inherit = False
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(theme.surface)
    shape.line.color.rgb = hex_to_rgb(theme.border_color)
    if theme.name != "academic":
        shape.adjustments[0] = 0.07


def render_closing_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="closing")
    add_brand(slide, theme)
    _add_panel(slide, theme)

    summary = data.body or data.subtitle or next(iter(data.bullets), None)
    add_text_box(
        slide, data.title, 1.60, 1.83 if summary else 2.44, 10.13, 1.78,
        theme.title_font, 38 if len(data.title) > 55 else 47, theme.title_color, True,
        align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE,
    )

    rule_y = 3.76 if summary else 4.44
    rule = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(6.12), Inches(rule_y), Inches(1.09), Inches(0.045),
    )
    rule.shadow.inherit = False
    rule.fill.solid()
    rule.fill.fore_color.rgb = hex_to_rgb(theme.primary if theme.name == "business" else theme.accent)
    rule.line.fill.background()

    if summary:
        add_text_box(
            slide, summary, 2.26, 4.01, 8.81, 1.95,
            theme.body_font, 20 if len(summary) > 190 else 24, theme.body_color,
            align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE,
        )

    add_footer(slide, theme)
    return slide
