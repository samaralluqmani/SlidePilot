from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from models.deck import Slide
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.text import add_bullet_list, add_text_box, hex_to_rgb
from presentation.components.visual import add_visual_panel
from presentation.theme import Theme


def render_content_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="content")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    text_x, text_y, text_w, text_h = 0.82, 2.45, 7.0, 3.95
    visual_x, visual_y, visual_w, visual_h = 8.42, 2.28, 3.92, 3.95

    if theme.name == "technology":
        panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.72), Inches(2.28), Inches(7.35), Inches(4.18))
        panel.fill.solid(); panel.fill.fore_color.rgb = hex_to_rgb(theme.surface); panel.fill.transparency = 4
        panel.line.color.rgb = hex_to_rgb(theme.border_color); panel.line.transparency = 35
    elif theme.name == "business":
        rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.98), Inches(2.35), Inches(0.018), Inches(3.85))
        rule.fill.solid(); rule.fill.fore_color.rgb = hex_to_rgb(theme.border_color); rule.line.fill.background()
    else:
        rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.82), Inches(2.28), Inches(7.0), Inches(0.018))
        rule.fill.solid(); rule.fill.fore_color.rgb = hex_to_rgb(theme.border_color); rule.line.fill.background()
        text_y = 2.58

    if data.bullets:
        add_bullet_list(slide, data.bullets, text_x, text_y, text_w, text_h, theme.body_font, 16, theme.body_color, theme.accent, 14)
    elif data.body:
        add_text_box(slide, data.body, text_x, text_y, text_w, text_h, theme.body_font, 17 if theme.name != "academic" else 16, theme.body_color)

    add_visual_panel(slide, theme, image_bytes, visual_x, visual_y, visual_w, visual_h, data.visual_caption)
    add_footer(slide, theme)
    return slide
