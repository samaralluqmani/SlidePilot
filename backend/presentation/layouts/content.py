from pptx.enum.text import MSO_ANCHOR

from models.deck import Slide
from presentation.components.card import add_card
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.text import add_bullet_list, add_text_box
from presentation.components.visual import add_visual_panel
from presentation.theme import Theme


def render_content_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme)
    add_brand(slide, theme)
    add_heading(slide, theme, data.title, data.subtitle)

    top = 2.55
    accent = theme.accent if theme.name == "technology" else theme.primary

    if image_bytes:
        if data.bullets:
            add_bullet_list(
                slide, data.bullets, 0.78, top + 0.2, 6.9, 3.55,
                theme.body_font, 18, theme.body_color, accent, 13,
            )
        elif data.body:
            add_text_box(
                slide, data.body, 0.78, top, 6.9, 3.6,
                theme.body_font, 22, theme.body_color, valign=MSO_ANCHOR.MIDDLE,
            )
        add_visual_panel(slide, theme, image_bytes, 8.1, top, 4.45, 3.63, data.visual_caption)
    elif data.bullets:
        columns = min(len(data.bullets), 3)
        rows = (len(data.bullets) + columns - 1) // columns
        gap = 0.23
        width = (11.77 - gap * (columns - 1)) / columns
        height = 1.68 if rows == 2 else 2.7
        for index, item in enumerate(data.bullets):
            row, column = divmod(index, columns)
            x = 0.78 + column * (width + gap)
            y = top + row * (height + gap)
            add_card(slide, theme, x=x, y=y, w=width, h=height, shadow=False, accent_top=True)
            add_text_box(
                slide, f"{index + 1:02d}", x + 0.2, y + 0.12, 0.65, 0.34,
                theme.body_font, 12, accent, True,
            )
            add_text_box(
                slide, item, x + 0.2, y + 0.48, width - 0.4, height - 0.55,
                theme.body_font, 18 if rows == 2 else 22, theme.body_color,
                valign=MSO_ANCHOR.MIDDLE,
            )
    elif data.body:
        add_card(slide, theme, x=0.78, y=top, w=11.77, h=3.45, shadow=False, accent_top=True)
        add_text_box(
            slide, data.body, 1.22, top + 0.3, 10.89, 2.85,
            theme.body_font, 26, theme.body_color, valign=MSO_ANCHOR.MIDDLE,
        )

    add_footer(slide, theme)
    return slide
