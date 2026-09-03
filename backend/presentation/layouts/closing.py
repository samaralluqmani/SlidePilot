from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from models.deck import Slide
from presentation.components.chrome import apply_background, add_brand, add_footer
from presentation.components.text import add_text_box, hex_to_rgb
from presentation.components.visual import add_visual_panel
from presentation.theme import Theme


def render_closing_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="closing")
    add_brand(slide, theme, f"{theme.name} / END")

    title_y = 1.92 if theme.name != "academic" else 1.85
    add_text_box(slide, data.title, 0.88, title_y, 7.0, 1.2, theme.title_font, 34, theme.title_color, True)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.88), Inches(3.28), Inches(1.0), Inches(0.05))
    line.fill.solid(); line.fill.fore_color.rgb = hex_to_rgb(theme.accent if theme.name != "business" else theme.primary); line.line.fill.background()

    if data.body:
        add_text_box(slide, data.body, 0.88, 3.63, 6.85, 1.7, theme.body_font, 16, theme.body_color)

    add_visual_panel(slide, theme, image_bytes, 8.55, 1.65, 3.75, 4.65, data.visual_caption)
    add_text_box(slide, "Thank you", 0.88, 5.75, 2.2, 0.4, theme.title_font, 16, theme.primary if theme.name != "technology" else theme.accent, True)
    add_footer(slide, theme)
    return slide
