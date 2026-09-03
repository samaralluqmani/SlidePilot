from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from PIL import Image
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches


ImageSource = str | Path | BytesIO | BinaryIO


def _prepare_cover_image(image_source: ImageSource, target_ratio: float) -> BytesIO:
    """Crop an image to fill a target frame without stretching it."""
    image = Image.open(image_source).convert("RGB")
    width, height = image.size
    image_ratio = width / height

    if image_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    elif image_ratio < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))

    output = BytesIO()
    image.save(output, format="JPEG", quality=94)
    output.seek(0)
    return output


def add_cover_image(slide, image_source: ImageSource, *, x: float, y: float, width: float, height: float):
    prepared = _prepare_cover_image(image_source, width / height)
    return slide.shapes.add_picture(prepared, Inches(x), Inches(y), Inches(width), Inches(height))


def add_framed_image(
    slide,
    image_source: ImageSource,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    border_color: RGBColor | None = None,
    border_width: float = 0.0,
    shadow: bool = False,
):
    """Clean image treatment with no white backing box."""
    if shadow:
        shadow_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(x + 0.045), Inches(y + 0.055), Inches(width), Inches(height),
        )
        shadow_shape.fill.solid()
        shadow_shape.fill.fore_color.rgb = RGBColor(15, 23, 42)
        shadow_shape.fill.transparency = 94
        shadow_shape.line.fill.background()

    picture = add_cover_image(slide, image_source, x=x, y=y, width=width, height=height)
    if border_color and border_width > 0:
        picture.line.color.rgb = border_color
        picture.line.width = Inches(border_width)
    return picture
