import math

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from models.deck import Slide
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.text import hex_to_rgb
from presentation.theme import Theme, contrasting_text


def _column_weights(headers: list[str], rows: list[list[str]]) -> list[float]:
    weights: list[float] = []
    for index, header in enumerate(headers):
        samples = [str(header)] + [str(row[index]) for row in rows if index < len(row)]
        longest = max((len(x) for x in samples), default=8)
        avg = sum(len(x) for x in samples) / max(len(samples), 1)
        weights.append(max(0.72, min(2.55, 0.60 + longest / 30 + avg / 62)))
    total = sum(weights) or 1
    return [w / total for w in weights]


def _font_size(headers: list[str], rows: list[list[str]]) -> float:
    longest = max((len(str(cell)) for row in rows for cell in row), default=0)
    row_count = len(rows)
    col_count = len(headers)

    if col_count >= 5 or row_count >= 7 or longest > 88:
        return 7.4
    if col_count == 4 or row_count >= 6 or longest > 62:
        return 8.0
    if longest > 42:
        return 8.6
    return 9.2


def _estimated_lines(text: str, width_inches: float, font_size: float) -> int:
    # Conservative PowerPoint text-fit heuristic. Narrow columns get fewer characters per line.
    chars_per_line = max(int(width_inches * (12.2 - max(font_size - 8.0, 0) * 0.45)), 7)
    return max(1, math.ceil(max(len(text), 1) / chars_per_line))


def render_table_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="data")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    if not data.table or not data.table.headers:
        add_footer(slide, theme, "STRUCTURED DATA")
        return slide

    headers = data.table.headers[:5]
    rows = [row[: len(headers)] for row in data.table.rows[:7]]

    x, y, total_w, total_h = 0.80, 2.56, 11.72, 3.88
    table_shape = slide.shapes.add_table(
        len(rows) + 1, len(headers), Inches(x), Inches(y), Inches(total_w), Inches(total_h)
    )
    table = table_shape.table

    weights = _column_weights(headers, rows)
    col_widths = [total_w * weight for weight in weights]
    for i, width in enumerate(col_widths):
        table.columns[i].width = Inches(width)

    header_fill = theme.primary
    header_text = contrasting_text(header_fill)

    body_size = _font_size(headers, rows)

    # Row heights adapt to the amount of wrapped text instead of forcing every row equal.
    header_h = 0.48
    body_available = total_h - header_h
    row_weights: list[float] = []
    for row in rows:
        max_lines = 1
        for col_index in range(len(headers)):
            value = str(row[col_index]) if col_index < len(row) else ""
            max_lines = max(max_lines, _estimated_lines(value, col_widths[col_index], body_size))
        row_weights.append(1.0 + max(0, max_lines - 1) * 0.62)

    total_row_weight = sum(row_weights) or 1.0
    table.rows[0].height = Inches(header_h)
    for row_index, weight in enumerate(row_weights, start=1):
        table.rows[row_index].height = Inches(body_available * weight / total_row_weight)

    for col_index, header in enumerate(headers):
        cell = table.cell(0, col_index)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(header_fill)
        cell.margin_left = Inches(0.11)
        cell.margin_right = Inches(0.11)
        cell.margin_top = Inches(0.05)
        cell.margin_bottom = Inches(0.05)
        cell.text_frame.word_wrap = True
        cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if col_index == 0 else PP_ALIGN.CENTER
        p.font.name = theme.body_font
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = hex_to_rgb(header_text)

    for row_index, row in enumerate(rows, start=1):
        for col_index in range(len(headers)):
            value = str(row[col_index]) if col_index < len(row) else ""
            cell = table.cell(row_index, col_index)
            cell.text = value
            cell.fill.solid()

            fill_color = theme.surface if row_index % 2 else theme.surface_alt
            cell.fill.fore_color.rgb = hex_to_rgb(fill_color)

            cell.margin_left = Inches(0.10)
            cell.margin_right = Inches(0.10)
            cell.margin_top = Inches(0.035)
            cell.margin_bottom = Inches(0.035)
            cell.text_frame.word_wrap = True
            cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if col_index in (0, len(headers) - 1) else PP_ALIGN.CENTER
            p.font.name = theme.body_font
            p.font.size = Pt(body_size)
            p.font.color.rgb = hex_to_rgb(theme.body_color)
            if col_index == 0:
                p.font.bold = True

    add_footer(slide, theme, "STRUCTURED DATA")
    return slide
