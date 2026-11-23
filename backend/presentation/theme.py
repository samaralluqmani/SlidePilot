from dataclasses import dataclass, replace
import re

from models.deck import ArtDirection

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

# Topic palettes inherit the typography and layout treatments of the base themes.
CULINARY_THEME = replace(
    ACADEMIC_THEME,
    background="FFF3E4", surface="FFF9EE", surface_alt="F6E2D0",
    primary="9C3B24", secondary="43532F", accent="AE631F",
    title_color="462719", body_color="513A2C", muted_color="735443", border_color="DFC0A8",
)

TRAVEL_THEME = replace(
    BUSINESS_THEME,
    background="EAF5F3", surface="F7FCFA", surface_alt="D9ECE8",
    primary="125D60", secondary="284A63", accent="A85B25",
    title_color="153C44", body_color="294951", muted_color="4A6469", border_color="A9CECA",
)

NATURE_THEME = replace(
    ACADEMIC_THEME,
    background="EBF0E1", surface="F6F8EF", surface_alt="DEE8D5",
    primary="34563A", secondary="5A5431", accent="8D651F",
    title_color="243A27", body_color="394D3A", muted_color="526651", border_color="B6C9A8",
)

CULTURE_THEME = replace(
    ACADEMIC_THEME,
    background="F3EAF2", surface="FCF6F9", surface_alt="EBD9E7",
    primary="76365D", secondary="4E3E6B", accent="9E5B27",
    title_color="40253A", body_color="51384D", muted_color="71536A", border_color="D9BBCF",
)

EDITORIAL_THEME = replace(
    BUSINESS_THEME,
    background="EEF0F5", surface="FAFBFE", surface_alt="E0E5F0",
    primary="4C4771", secondary="3C5968", accent="356879",
    title_color="302E49", body_color="41455A", muted_color="585D72", border_color="C4CADE",
)

THEMES = {
    "technology": TECHNOLOGY_THEME,
    "business": BUSINESS_THEME,
    "academic": ACADEMIC_THEME,
    "culinary": CULINARY_THEME,
    "travel": TRAVEL_THEME,
    "nature": NATURE_THEME,
    "culture": CULTURE_THEME,
    "editorial": EDITORIAL_THEME,
}


def get_theme(name: str) -> Theme:
    return THEMES.get(name, TECHNOLOGY_THEME)


def _channels(color: str) -> tuple[int, int, int]:
    return tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))


def _mix(color: str, target: str, amount: float) -> str:
    return "".join(
        f"{round(start + (end - start) * amount):02X}"
        for start, end in zip(_channels(color), _channels(target))
    )


def _luminance(color: str) -> float:
    values = [channel / 255 for channel in _channels(color)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast_ratio(first: str, second: str) -> float:
    low, high = sorted((_luminance(first), _luminance(second)))
    return (high + 0.05) / (low + 0.05)


def contrasting_text(background: str) -> str:
    return max(("FFFFFF", "000000"), key=lambda color: contrast_ratio(color, background))


def _readable(color: str, target: str, surfaces: tuple[str, ...]) -> str:
    for step in range(21):
        candidate = _mix(color, target, step / 20)
        if all(contrast_ratio(candidate, surface) >= 4.5 for surface in surfaces):
            return candidate
    return target


def get_deck_theme(name: str, direction: ArtDirection | None) -> Theme:
    fallback = get_theme(name)
    if direction is None:
        return fallback

    primary, accent = (value.strip().removeprefix("#").upper() for value in (direction.primary, direction.accent))
    if not all(re.fullmatch(r"[0-9A-F]{6}", color) for color in (primary, accent)):
        return fallback

    dark = direction.canvas == "dark"
    neutral = "10131E" if dark else "FAF9F6"
    foreground = "FFFFFF" if dark else "000000"
    background = _mix(neutral, primary, 0.08)
    surface = _mix(neutral, primary, 0.14 if dark else 0.03)
    surface_alt = _mix(neutral, accent, 0.20 if dark else 0.10)
    surfaces = (background, surface, surface_alt)

    # Keep light/dark layout treatments consistent with the generated canvas.
    base = TECHNOLOGY_THEME if dark else (ACADEMIC_THEME if fallback.name == "academic" else BUSINESS_THEME)
    return replace(
        base,
        background=background,
        surface=surface,
        surface_alt=surface_alt,
        primary=_readable(primary, foreground, surfaces),
        secondary=_readable(_mix(primary, accent, 0.5), foreground, surfaces),
        accent=_readable(accent, foreground, surfaces),
        title_color=_readable(_mix(foreground, primary, 0.12), foreground, surfaces),
        body_color=_readable(_mix(foreground, primary, 0.24), foreground, surfaces),
        muted_color=_readable(_mix(foreground, background, 0.42), foreground, surfaces),
        border_color=_mix(surface, foreground, 0.23),
    )
