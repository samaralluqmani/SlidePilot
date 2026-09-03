import os
import re
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from presentation.builder import build_presentation
from presentation.intelligence.content_validator import validate_deck_content
from presentation.intelligence.layout_validator import validate_deck_layouts
from presentation.intelligence.theme_resolver import resolve_theme
from services.ai_planner import create_deck
from services.document_parser import SUPPORTED_EXTENSIONS, extract_text
from services.visual_service import generate_deck_visuals


load_dotenv()

app = FastAPI(
    title="SlidePilot API",
    description="Document-to-presentation generation backend for SlidePilot.",
    version="2.0.0",
)

origins = [
    x.strip()
    for x in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if x.strip()
]

# Also allow private-network development addresses such as
# http://192.168.x.x:3000, which Next.js may show when opened over LAN.
local_origin_regex = os.getenv(
    "FRONTEND_ORIGIN_REGEX",
    r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?$",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=local_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-SlidePilot-Theme", "X-SlidePilot-Slides"],
)


def _extension(filename: str) -> str:
    return filename.lower().rsplit(".", 1)[-1] if "." in filename else ""


def _validate_upload(filename: str | None, file_bytes: bytes) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="File name is missing.")

    extension = _extension(filename)
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported.")

    max_bytes = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File is too large. Maximum size is {os.getenv('MAX_UPLOAD_MB', '20')} MB.")
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    return extension


def _safe_filename(filename: str) -> str:
    stem = Path(filename).stem
    safe = re.sub(r"[^A-Za-z0-9._ -]+", "", stem).strip() or "slidepilot"
    return f"{safe}_presentation.pptx"


def _prepare_deck(text: str, theme_override: str | None):
    deck = create_deck(text)
    deck = resolve_theme(deck, text, theme_override)
    deck = validate_deck_layouts(deck)
    deck = validate_deck_content(deck)
    return deck


@app.get("/")
def root():
    return {"message": "SlidePilot API is running", "version": "2.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/documents/extract")
async def extract_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        extension = _validate_upload(file.filename, file_bytes)
        text = extract_text(file.filename or "", file_bytes)
        if not text.strip():
            raise HTTPException(status_code=422, detail="No readable text was found in the document.")
        return {
            "success": True,
            "filename": file.filename,
            "file_type": extension,
            "characters": len(text),
            "preview": text[:1200],
        }
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Could not process document: {error}") from error


@app.post("/presentations/plan")
async def plan_presentation(
    file: UploadFile = File(...),
    theme_override: str = Form("auto"),
):
    try:
        file_bytes = await file.read()
        _validate_upload(file.filename, file_bytes)
        text = extract_text(file.filename or "", file_bytes)
        if not text.strip():
            raise HTTPException(status_code=422, detail="No readable text was found in the document.")

        override = None if theme_override == "auto" else theme_override
        deck = await run_in_threadpool(_prepare_deck, text, override)
        return {"success": True, "filename": file.filename, "deck": deck.model_dump()}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Could not create presentation plan: {error}") from error


@app.post("/presentations/generate")
async def generate_presentation(
    file: UploadFile = File(...),
    theme_override: str = Form("auto"),
):
    try:
        file_bytes = await file.read()
        _validate_upload(file.filename, file_bytes)
        text = extract_text(file.filename or "", file_bytes)
        if not text.strip():
            raise HTTPException(status_code=422, detail="No readable text was found in the document.")

        override = None if theme_override == "auto" else theme_override
        deck = await run_in_threadpool(_prepare_deck, text, override)
        visuals = await run_in_threadpool(generate_deck_visuals, deck)
        pptx_file = await run_in_threadpool(build_presentation, deck, visuals)

        output_filename = _safe_filename(file.filename or "slidepilot")
        ascii_fallback = "slidepilot_presentation.pptx"
        disposition = f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quote(output_filename)}"

        return StreamingResponse(
            pptx_file,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": disposition,
                "X-SlidePilot-Theme": deck.theme,
                "X-SlidePilot-Slides": str(len(deck.slides)),
            },
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Could not generate presentation: {error}") from error
