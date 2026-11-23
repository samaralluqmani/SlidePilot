from io import BytesIO

from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

from presentation.components.image_frame import add_framed_image
from presentation.components.text import add_text_box, hex_to_rgb
from presentation.theme import Theme


def _corner_bracket(slide, x: float, y: float, w: float, h: float, color: str, alpha: int = 20):
    """Draw four small corner marks without placing a card behind the image."""
    length = 0.32
    thickness = 0.018
    pieces = [
        (x - 0.03, y - 0.03, length, thickness),
        (x - 0.03, y - 0.03, thickness, length),
        (x + w - length + 0.03, y - 0.03, length, thickness),
        (x + w + 0.012, y - 0.03, thickness, length),
        (x - 0.03, y + h + 0.012, length, thickness),
        (x - 0.03, y + h - length + 0.03, thickness, length),
        (x + w - length + 0.03, y + h + 0.012, length, thickness),
        (x + w + 0.012, y + h - length + 0.03, thickness, length),
    ]
    for px, py, pw, ph in pieces:
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(px), Inches(py), Inches(pw), Inches(ph),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = hex_to_rgb(color)
        shape.fill.transparency = alpha
        shape.line.fill.background()


def add_visual_panel(
    slide,
    theme: Theme,
    image_bytes: bytes | None,
    x: float,
    y: float,
    w: float,
    h: float,
    caption: str | None = None,
):
    """Theme-aware visual area.

    Generated imagery is never placed on a backing card. The theme difference comes
    from framing, border, and corner treatment only. A panel is created only when
    image generation is unavailable and a deterministic fallback visual is needed.
    """
    frame = None

    if image_bytes:
        if theme.name == "business":
            add_framed_image(
                slide, BytesIO(image_bytes),
                x=x, y=y, width=w, height=h,
                shadow=True,
            )
        elif theme.name == "technology":
            add_framed_image(
                slide, BytesIO(image_bytes),
                x=x, y=y, width=w, height=h,
                border_color=hex_to_rgb(theme.accent),
                border_width=0.010,
                shadow=False,
            )
            _corner_bracket(slide, x, y, w, h, theme.accent, 18)
        else:
            add_framed_image(
                slide, BytesIO(image_bytes),
                x=x, y=y, width=w, height=h,
                border_color=hex_to_rgb(theme.border_color),
                border_width=0.008,
                shadow=False,
            )
            # Academic imagery gets one restrained editorial rule, not a card.
            rule = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x + 0.20), Inches(y + h + 0.045), Inches(min(w * 0.42, 1.45)), Inches(0.020),
            )
            rule.fill.solid()
            rule.fill.fore_color.rgb = hex_to_rgb(theme.accent)
            rule.fill.transparency = 22
            rule.line.fill.background()

    else:
        frame = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(y), Inches(w), Inches(h),
        )
        frame.fill.solid()
        frame.fill.fore_color.rgb = hex_to_rgb(theme.surface_alt)
        frame.line.color.rgb = hex_to_rgb(theme.border_color)
        frame.line.transparency = 45 if theme.name == "technology" else 28

        # Deterministic fallback illustration when image generation fails.
        if theme.name == "technology":
            for index, scale in enumerate((0.62, 0.40, 0.22)):
                orb = slide.shapes.add_shape(
                    MSO_SHAPE.OVAL,
                    Inches(x + w * (0.18 + index * 0.15)),
                    Inches(y + h * (0.15 + index * 0.13)),
                    Inches(w * scale), Inches(w * scale),
                )
                orb.fill.solid()
                orb.fill.fore_color.rgb = hex_to_rgb(theme.primary if index != 1 else theme.accent)
                orb.fill.transparency = 30 + index * 14
                orb.line.fill.background()
        elif theme.name == "business":
            for index, scale in enumerate((0.75, 0.52, 0.29)):
                size = min(w, h) * scale
                tile = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(x + (w - size) / 2), Inches(y + (h - size) / 2),
                    Inches(size), Inches(size),
                )
                tile.rotation = 45
                tile.fill.solid()
                tile.fill.fore_color.rgb = hex_to_rgb((theme.border_color, theme.accent, theme.primary)[index])
                tile.line.fill.background()
        else:
            book = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x + 0.62), Inches(y + 0.65), Inches(w - 1.24), Inches(h - 1.3),
            )
            book.fill.solid()
            book.fill.fore_color.rgb = hex_to_rgb(theme.surface)
            book.line.color.rgb = hex_to_rgb(theme.border_color)
            for i in range(4):
                line = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE,
                    Inches(x + 1.0), Inches(y + 1.2 + i * 0.55), Inches(w - 2.0), Inches(0.025),
                )
                line.fill.solid()
                line.fill.fore_color.rgb = hex_to_rgb(theme.border_color)
                line.line.fill.background()

    if caption:
        add_text_box(
            slide, caption,
            x + 0.12, y + h + 0.08, w - 0.24, 0.28,
            theme.body_font, 8, theme.muted_color,
        )
    return frame
