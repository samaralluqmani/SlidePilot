import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

from models.deck import Deck


load_dotenv()

SKIP_LAYOUTS = {"metrics", "table", "chart", "timeline", "process"}


THEME_VISUAL_DIRECTION = {
    "business": (
        "Premium corporate editorial photography or sophisticated conceptual imagery. "
        "Use clean architectural geometry, executive environments, market/growth metaphors, "
        "natural professional lighting, restrained blue-neutral palette, realistic materials, "
        "high-end consulting-report aesthetic, and generous negative space. Avoid generic stock-photo poses."
    ),
    "technology": (
        "Cinematic modern technology imagery with a dark navy foundation, controlled cyan and violet illumination, "
        "precise data-flow or network motifs, dimensional depth, premium product-visualization quality, "
        "and clean negative space. Avoid busy sci-fi interfaces, readable UI text, robots, and cliché hologram dashboards."
    ),
    "academic": (
        "Refined scholarly editorial imagery with warm ivory, muted burgundy, bronze/gold accents, "
        "research, learning, books, laboratories, campuses, or abstract knowledge structures as appropriate. "
        "Use calm natural light, restrained composition, documentary/editorial credibility, and generous negative space. "
        "Avoid corporate stock-photo styling."
    ),
}


def _client() -> OpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to backend/.env.")
    return OpenAI()


def generate_deck_visuals(deck: Deck) -> dict[int, bytes]:
    """Generate visuals automatically for suitable story slides. Failures remain non-fatal."""
    max_visuals = int(os.getenv("MAX_GENERATED_VISUALS", "6"))
    reasoning_model = os.getenv("OPENAI_VISUAL_REASONING_MODEL", "gpt-5.6-luna")
    image_model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")
    client = _client()

    visuals: dict[int, bytes] = {}
    generated = 0
    theme_direction = THEME_VISUAL_DIRECTION.get(deck.theme, THEME_VISUAL_DIRECTION["technology"])

    for index, slide in enumerate(deck.slides):
        if generated >= max_visuals:
            break
        if slide.layout in SKIP_LAYOUTS:
            continue
        if slide.visual_style == "none" or not slide.visual_prompt:
            continue

        prompt = (
            f"Create one premium presentation visual for a {deck.theme} presentation. "
            f"Slide title: {slide.title}. Content-specific direction: {slide.visual_prompt}. "
            f"Theme art direction: {theme_direction} "
            "Compose for a portrait-ish side visual region inside a 16:9 presentation slide, with a clear focal subject "
            "and useful breathing room around it. No readable text, no letters, no logos, no watermark."
        )

        try:
            response = client.responses.create(
                model=reasoning_model,
                input=prompt,
                tools=[
                    {
                        "type": "image_generation",
                        "model": image_model,
                        "size": "1536x1024",
                        "quality": "medium",
                        "output_format": "png",
                    }
                ],
            )

            for item in response.output:
                if getattr(item, "type", None) == "image_generation_call" and getattr(item, "result", None):
                    visuals[index] = base64.b64decode(item.result)
                    generated += 1
                    break
        except Exception:
            # Image generation should never prevent the PPTX from being delivered.
            continue

    return visuals
