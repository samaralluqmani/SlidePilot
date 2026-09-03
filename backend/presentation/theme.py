from dataclasses import dataclass

from presentation.tokens import Radius, Spacing, Typography


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    surface: str
    surface_alt: str
    primary: str
    secondary: str
    accent: str
    title_color: str
    body_color: str
    muted_color: str
    border_color: str
    title_font: str
    body_font: str
    typography: Typography = Typography()
    spacing: Spacing = Spacing()
    radius: Radius = Radius()


TECHNOLOGY_THEME = Theme(
    name="technology",
    background="07111F",
    surface="0D1B2A",
    surface_alt="111E31",
    primary="7C3AED",
    secondary="2563EB",
    accent="22D3EE",
    title_color="FFFFFF",
    body_color="D5DEEA",
    muted_color="94A3B8",
    border_color="263750",
    title_font="Aptos Display",
    body_font="Aptos",
)

BUSINESS_THEME = Theme(
    name="business",
    background="F7F8FC",
    surface="FFFFFF",
    surface_alt="EEF3FF",
    primary="1D4ED8",
    secondary="334155",
    accent="0EA5E9",
    title_color="111827",
    body_color="374151",
    muted_color="6B7280",
    border_color="D8E0ED",
    title_font="Aptos Display",
    body_font="Aptos",
)

ACADEMIC_THEME = Theme(
    name="academic",
    background="F8F5EE",
    surface="FFFDF8",
    surface_alt="F1E9DC",
    primary="7C2D12",
    secondary="92400E",
    accent="C58B2A",
    title_color="2B2118",
    body_color="4B4037",
    muted_color="786C61",
    border_color="D8CDBD",
    title_font="Georgia",
    body_font="Aptos",
)

THEMES = {
    "technology": TECHNOLOGY_THEME,
    "business": BUSINESS_THEME,
    "academic": ACADEMIC_THEME,
}


def get_theme(name: str) -> Theme:
    return THEMES.get(name, TECHNOLOGY_THEME)
