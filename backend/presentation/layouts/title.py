from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches

from models.deck import Slide
from presentation.components.chrome import apply_background, add_brand, add_footer
from presentation.components.text import add_text_box, hex_to_rgb
from presentation.components.visual import add_visual_panel
from presentation.theme import Theme


def render_title_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="cover")

    section = f"{theme.name.upper()} / 01"
    add_brand(slide, theme, section)

    if theme.name == "technology":
        title_x, title_y, title_w = 0.88, 2.0, 7.0
        visual_x, visual_y, visual_w, visual_h = 8.55, 1.45, 3.85, 4.75
        title_size = 40
        accent_color = theme.accent
    elif theme.name == "business":
        title_x, title_y, title_w = 0.82, 2.0, 7.0
        visual_x, visual_y, visual_w, visual_h = 8.45, 1.45, 3.95, 4.8
        title_size = 36
        accent_color = theme.primary
    else:
        title_x, title_y, title_w = 0.82, 1.92, 7.3
        visual_x, visual_y, visual_w, visual_h = 8.55, 1.58, 3.75, 4.7
        title_size = 35
        accent_color = theme.accent

    add_text_box(slide, data.title, title_x, title_y - 0.25, title_w, 1.75, theme.title_font,
                 title_size - 6 if len(data.title) > 50 else title_size + 4,
                 theme.title_color, True, valign=MSO_ANCHOR.MIDDLE)

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(title_x), Inches(3.73), Inches(1.15), Inches(0.055))
    line.fill.solid(); line.fill.fore_color.rgb = hex_to_rgb(accent_color); line.line.fill.background()

    if data.subtitle:
        add_text_box(slide, data.subtitle, title_x, 4.03, 6.7, 0.85, theme.body_font, 17, theme.body_color)

    caption = data.visual_caption if image_bytes and theme.name == "academic" else None
    add_visual_panel(slide, theme, image_bytes, visual_x, visual_y, visual_w, visual_h, caption)

    add_footer(slide, theme)
    return slide
