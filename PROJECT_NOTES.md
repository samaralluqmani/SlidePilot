# SlidePilot v2 — Project Notes

## Main cleanup decisions

- Removed the duplicated legacy title/content functions from the rendering path.
- Removed separate `business_*` layout files and replaced them with shared theme-aware renderers.
- Corrected `.gitgnore` to `.gitignore`.
- Corrected the empty `frontedend` folder to a complete `frontend` Next.js app.
- Corrected `puthon-pptx` to `python-pptx` in requirements.
- Added CORS, file-size validation, safer filenames, theme override, and a planning endpoint.
- Added visual-planning fields to the deck schema and optional OpenAI image generation.
- Added DOCX table extraction so structured source tables are not silently lost.
- Kept generated images optional: data-heavy slides rely on charts/tables/metrics rather than decorative pictures.

## Backend pipeline

`Document -> Extract -> AI Deck -> Theme Resolver -> Layout Validator -> Content Validator -> Optional Visuals -> PPTX Builder`

## Presentation design languages

- Technology: dark, cyan/purple, futuristic surfaces.
- Business: light, blue corporate rail, minimal cards and grids.
- Academic: warm editorial canvas, burgundy/gold, serif hierarchy.
