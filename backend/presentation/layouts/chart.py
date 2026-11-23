from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

from models.deck import Slide
from presentation.components.chrome import apply_background, add_brand, add_footer, add_heading
from presentation.components.text import hex_to_rgb
from presentation.theme import Theme


def _chart_surface(slide, theme: Theme):
    if theme.name == "academic":
        card = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.82), Inches(2.25), Inches(11.7), Inches(4.25),
        )
        card.fill.solid()
        card.fill.fore_color.rgb = hex_to_rgb(theme.surface)
        card.line.color.rgb = hex_to_rgb(theme.border_color)
        card.line.transparency = 45

        rule = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.82), Inches(2.25), Inches(2.15), Inches(0.030),
        )
        rule.fill.solid()
        rule.fill.fore_color.rgb = hex_to_rgb(theme.accent)
        rule.line.fill.background()
        return card

    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.82), Inches(2.25), Inches(11.7), Inches(4.25),
    )
    card.fill.solid()
    card.fill.fore_color.rgb = hex_to_rgb(theme.surface)
    card.fill.transparency = 5 if theme.name == "technology" else 0
    card.line.color.rgb = hex_to_rgb(theme.accent if theme.name == "technology" else theme.border_color)
    card.line.transparency = 68 if theme.name == "technology" else 45
    return card


def render_chart_slide(prs, data: Slide, theme: Theme, image_bytes: bytes | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide, theme, variant="data")
    add_brand(slide, theme, theme.name)
    add_heading(slide, theme, data.title, data.subtitle)

    if not data.chart or not data.chart.labels or not data.chart.values:
        add_footer(slide, theme)
        return slide

    _chart_surface(slide, theme)

    chart_data = ChartData()
    chart_data.categories = data.chart.labels
    chart_data.add_series("Value", data.chart.values)

    chart_type_map = {
        "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
        "line": XL_CHART_TYPE.LINE_MARKERS,
        "pie": XL_CHART_TYPE.PIE,
    }
    chart_type = chart_type_map.get(data.chart.chart_type, XL_CHART_TYPE.COLUMN_CLUSTERED)
    chart = slide.shapes.add_chart(
        chart_type,
        Inches(1.12), Inches(2.55), Inches(11.0), Inches(3.55),
        chart_data,
    ).chart

    chart.has_title = False
    chart.has_legend = data.chart.chart_type == "pie"
    if chart.has_legend:
        chart.legend.position = XL_LEGEND_POSITION.RIGHT
        chart.legend.font.name = theme.body_font
        chart.legend.font.size = Pt(12)
        chart.legend.font.color.rgb = hex_to_rgb(theme.body_color)

    series = chart.series[0]
    series_color = theme.accent if theme.name == "technology" else theme.primary
    if data.chart.chart_type == "line":
        series.format.line.color.rgb = hex_to_rgb(series_color)
        series.format.line.width = Pt(2.25)
    elif data.chart.chart_type == "bar":
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = hex_to_rgb(series_color)
        series.format.line.color.rgb = hex_to_rgb(series_color)

    if data.chart.chart_type == "pie":
        colors = (theme.primary, theme.accent, theme.secondary, theme.muted_color)
        for index, point in enumerate(series.points):
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = hex_to_rgb(colors[index % len(colors)])
            point.format.line.color.rgb = hex_to_rgb(theme.surface)
    else:
        value_axis = chart.value_axis
        value_axis.has_major_gridlines = True
        value_axis.tick_labels.font.name = theme.body_font
        value_axis.tick_labels.font.size = Pt(12)
        value_axis.tick_labels.font.color.rgb = hex_to_rgb(theme.muted_color)

        category_axis = chart.category_axis
        category_axis.tick_labels.font.name = theme.body_font
        category_axis.tick_labels.font.size = Pt(11 if len(data.chart.labels) > 5 else 12)
        category_axis.tick_labels.font.color.rgb = hex_to_rgb(theme.body_color)

    add_footer(slide, theme, f"{data.chart.chart_type.upper()} VISUALIZATION")
    return slide
