# SlidePilot

SlidePilot turns PDF, DOCX, and TXT documents into editable PowerPoint presentations using a Python/FastAPI backend and a Next.js frontend.

## What is included

- PDF, DOCX, and TXT text extraction
- Structured presentation planning with OpenAI Structured Outputs
- 10 slide layouts: title, content, bullets, two-column, metrics, process, timeline, table, chart, closing
- Presentation intelligence: theme resolution, layout validation, and content limits
- Three distinct design languages: Technology, Business, Academic
- Optional AI-generated visuals for suitable story slides
- Editable PPTX output with python-pptx
- Drag-and-drop Next.js interface that generates PowerPoint after upload

## Project structure

```text
SlidePilot/
├── backend/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── presentation/
│       ├── components/
│       ├── intelligence/
│       └── layouts/
├── frontend/
│   └── app/
├── start-backend.bat
└── start-frontend.bat
```

## 1. Backend setup (Windows)

Open CMD in `SlidePilot/backend`:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and replace:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Then run:

```cmd
uvicorn main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## 2. Frontend setup

Open a second CMD in `SlidePilot/frontend`:

```cmd
npm install
copy .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## AI visuals

SlidePilot generates images automatically for slides where an editorial image adds value. Charts, tables, metrics, and timelines use their own information visualizations instead.

Environment controls:

```env
OPENAI_TEXT_MODEL=gpt-5.6-luna
OPENAI_VISUAL_REASONING_MODEL=gpt-5.6-luna
OPENAI_IMAGE_MODEL=gpt-image-2
MAX_GENERATED_VISUALS=6
```

## Themes

- **Technology:** dark navy, cyan/purple accents, glow and glass-like surfaces.
- **Business:** light corporate canvas, blue rail, restrained grids and KPI styling.
- **Academic:** warm editorial canvas, burgundy/gold rules, serif hierarchy.

- **Culinary:** cream, terracotta and warm editorial food imagery.
- **Travel:** sea-glass, deep teal and destination-led imagery.
- **Nature:** soft greens, earthy accents and natural-history imagery.
- **Culture:** plum, muted rose and arts editorial imagery.
- **Editorial:** slate, muted violet and subject-led imagery for general topics.

SlidePilot chooses a theme automatically based on the source document.
