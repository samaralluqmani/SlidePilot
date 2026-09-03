from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


def hex_to_rgb(hex_color: str) -> RGBColor:
    value = hex_color.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def add_text_box(
    slide,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font_name: str,
    font_size: int,
    color: str,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    font = paragraph.font
    font.name = font_name
    font.size = Pt(font_size)
    font.bold = bold
    font.color.rgb = hex_to_rgb(color)
    return box


def add_bullet_list(
    slide,
    items: list[str],
    x: float,
    y: float,
    width: float,
    height: float,
    font_name: str,
    font_size: int,
    color: str,
    accent: str,
    space_after: int = 13,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True

    for index, item in enumerate(items):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.text = f"•  {item}"
        p.font.name = font_name
        p.font.size = Pt(font_size)
        p.font.color.rgb = hex_to_rgb(color)
        p.space_after = Pt(space_after)

        # python-pptx does not support separately styling the bullet glyph on a simple paragraph,
        # so the theme accent is expressed through surrounding chrome rather than inline runs.
    return box
