import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

from models.deck import Deck


load_dotenv()

SKIP_LAYOUTS = {"metrics", "metric_story", "takeaway", "table", "chart", "timeline", "process", "two_column", "closing"}


THEME_VISUAL_DIRECTION = {
    "culinary": (
        "Natural culinary editorial photography with warm terracotta and cream, natural window light, "
        "realistic textures, and the specific dish or ingredients described by the source."
    ),
    "travel": (
        "Destination editorial photography with deep teal, sea-glass tones and warm sand. "
        "Use details tied to the named place or travel activity, with a clear focal point."
    ),
    "nature": "Natural history editorial imagery, muted greens, earthy accents and subject-specific detail.",
    "culture": "Arts editorial imagery with plum and muted rose, soft light, and subject-specific materials.",
    "editorial": "Clean topic-led editorial imagery with slate, muted violet and restrained blue-green accents.",
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
    client = None

    visuals: dict[int, bytes] = {}
    generated = 0
    theme_direction = THEME_VISUAL_DIRECTION.get(deck.theme, THEME_VISUAL_DIRECTION["editorial"])

    # Preserve the cover and evidence visuals when the document exceeds the image budget.
    ordered_slides = sorted(
        enumerate(deck.slides),
        key=lambda entry: ({"title": 0, "evidence": 1}.get(entry[1].layout, 2), entry[0]),
    )
    for index, slide in ordered_slides:
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
            "Compose for the right-hand image region of a presentation slide, with a centered focal subject "
            "and useful breathing room around it. No readable text, no letters, no logos, no watermark."
        )

        try:
            if client is None:
                client = _client()
            response = client.responses.create(
                model=reasoning_model,
                input=prompt,
                tools=[
                    {
                        "type": "image_generation",
                        "model": image_model,
                        "size": "1024x1536" if slide.layout == "title" else "1536x1024",
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
