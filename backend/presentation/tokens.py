from dataclasses import dataclass


@dataclass(frozen=True)
class Typography:
    hero: int = 38
    title: int = 28
    subtitle: int = 17
    body: int = 16
    small: int = 10


@dataclass(frozen=True)
class Spacing:
    margin_x: float = 0.8
    margin_y: float = 0.55
    gap_sm: float = 0.18
    gap_md: float = 0.35
    gap_lg: float = 0.65


@dataclass(frozen=True)
class Radius:
    sm: float = 0.10
    md: float = 0.18
    lg: float = 0.28
