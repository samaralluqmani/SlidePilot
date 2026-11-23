from pptx.enum.text import MSO_ANCHOR

from models.deck import Slide
from presentation.components.chrome import add_brand, add_footer, apply_background
from presentation.components.text import add_text_box
from presentation.theme import Theme


def render_takeaway_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme)
    add_brand(slide, theme)
    accent = theme.accent if theme.name == "technology" else theme.primary
    add_text_box(
        slide, data.title, 0.78, 1.32, 11.77, 2.25,
        theme.title_font, 40, accent, True, valign=MSO_ANCHOR.BOTTOM,
    )
    explanation = data.body or data.subtitle
    if explanation:
        add_text_box(
            slide, explanation, 0.78, 3.82, 11.77, 2.2,
            theme.body_font, 25, theme.body_color,
        )
    add_footer(slide, theme)
    return slide
