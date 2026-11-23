from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from models.deck import Slide
from presentation.components.card import add_card
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.text import add_bullet_list, add_text_box, hex_to_rgb
from presentation.theme import Theme, contrasting_text


def render_two_column_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="content")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    left_x, right_x, col_w = 0.82, 6.85, 5.55

    if theme.name in {"business", "technology"}:
        card_y, card_h, band_h = 2.52, 3.36, 0.48
        band_colors = (theme.primary, theme.secondary if theme.name == "technology" else theme.accent)
        for x, band_color in zip((left_x, right_x), band_colors):
            add_card(
                slide, theme, x=x, y=card_y, w=col_w, h=card_h,
                shadow=theme.name == "business",
            )
            band = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x), Inches(card_y), Inches(col_w), Inches(band_h),
            )
            band.fill.solid()
            band.fill.fore_color.rgb = hex_to_rgb(band_color)
            band.line.fill.background()
        left_heading_color, right_heading_color = map(contrasting_text, band_colors)
        title_y = card_y + 0.13
        items_y = card_y + 0.72
        items_h = 2.30
    else:
        divider = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(6.55), Inches(2.48), Inches(0.018), Inches(3.35),
        )
        divider.fill.solid()
        divider.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
        divider.line.fill.background()
        left_heading_color = right_heading_color = theme.primary
        title_y = 2.62
        items_y = 3.20
        items_h = 2.45

    add_text_box(slide, data.left_title or "Overview", left_x + 0.22, title_y, 4.95, 0.32, theme.body_font, 14, left_heading_color, True)
    add_text_box(slide, data.right_title or "Details", right_x + 0.22, title_y, 4.95, 0.32, theme.body_font, 14, right_heading_color, True)

    add_bullet_list(
        slide, data.left_items, left_x + 0.28, items_y, 4.85, items_h,
        theme.body_font, 13 if theme.name != "academic" else 14,
        theme.body_color, theme.accent, 10,
    )
    add_bullet_list(
        slide, data.right_items, right_x + 0.28, items_y, 4.85, items_h,
        theme.body_font, 13 if theme.name != "academic" else 14,
        theme.body_color, theme.accent, 10,
    )

    add_footer(slide, theme, "COMPARISON / STRUCTURE")
    return slide
