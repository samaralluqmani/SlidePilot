from unicodedata import bidirectional

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


def hex_to_rgb(hex_color: str) -> RGBColor:
    value = hex_color.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _text_frame(slide, x, y, width, height):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    # Retain the layout box and the editable text. PowerPoint shrinks only when needed.
    frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    return box, frame


def _style_paragraph(paragraph, text, font_name, font_size, color, bold=False, align=None):
    direction = [bidirectional(character) for character in text]
    first_strong = next((value for value in direction if value in {"L", "R", "AL"}), "L")
    rtl = first_strong in {"R", "AL"}

    paragraph.text = text
    paragraph.alignment = align if align is not None else (PP_ALIGN.RIGHT if rtl else PP_ALIGN.LEFT)
    properties = paragraph._p.get_or_add_pPr()
    if rtl:
        properties.set("rtl", "1")
    font = paragraph.font
    font.name = font_name
    font.size = Pt(font_size)
    font.bold = bold
    font.color.rgb = hex_to_rgb(color)

    if "AL" in direction or "R" in direction:
        complex_font = OxmlElement("a:cs")
        complex_font.set("typeface", "Arial")
        properties.get_or_add_defRPr().append(complex_font)
    return properties, rtl


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
    align=None,
    valign=MSO_ANCHOR.TOP,
):
    box, frame = _text_frame(slide, x, y, width, height)
    frame.vertical_anchor = valign
    _style_paragraph(frame.paragraphs[0], text, font_name, font_size, color, bold, align)
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
    box, frame = _text_frame(slide, x, y, width, height)

    for index, item in enumerate(items):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.space_after = Pt(space_after if index < len(items) - 1 else 0)
        properties, rtl = _style_paragraph(paragraph, item, font_name, font_size, color)
        properties.set("marR" if rtl else "marL", str(Pt(14)))
        properties.set("indent", str(Pt(-12)))
        bullet = OxmlElement("a:buChar")
        bullet.set("char", "•")
        properties.insert_element_before(bullet, "a:defRPr")
    return box
