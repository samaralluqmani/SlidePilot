"use client";

import { type DragEvent, useMemo, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const ALLOWED = ["pdf", "docx", "txt"];
const MAX_BYTES = 20 * 1024 * 1024;

type ThemeChoice = "auto" | "technology" | "business" | "academic";
type Status = "idle" | "working" | "ready" | "error";

function fileExtension(name: string) {
  return name.split(".").pop()?.toLowerCase() ?? "";
}

function parseFilename(disposition: string | null) {
  if (!disposition) return "slidepilot_presentation.pptx";
  const utf = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf?.[1]) return decodeURIComponent(utf[1]);
  const plain = disposition.match(/filename="?([^";]+)"?/i);
  return plain?.[1] ?? "slidepilot_presentation.pptx";
}

export default function Home() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [theme, setTheme] = useState<ThemeChoice>("auto");
  const [status, setStatus] = useState<Status>("idle");
  const [phase, setPhase] = useState(0);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [downloadName, setDownloadName] = useState("slidepilot_presentation.pptx");
  const [resultMeta, setResultMeta] = useState<{ theme?: string; slides?: string }>({});

  const phases = useMemo(() => [
    "Reading document",
    "Planning slide story",
    "Applying design system",
    "Generating AI visuals",
    "Building PowerPoint",
  ], []);

  function chooseFile(candidate: File | null) {
    setError("");
    setDownloadUrl((old) => {
      if (old) URL.revokeObjectURL(old);
      return null;
    });
    setStatus("idle");
    if (!candidate) return setFile(null);

    const ext = fileExtension(candidate.name);
    if (!ALLOWED.includes(ext)) {
      setFile(null);
      setError("Please choose a PDF, DOCX, or TXT file.");
      return;
    }
    if (candidate.size > MAX_BYTES) {
      setFile(null);
      setError("The file is larger than 20 MB.");
      return;
    }
    setFile(candidate);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    chooseFile(event.dataTransfer.files?.[0] ?? null);
  }

  async function generate() {
    const selectedFile = file ?? inputRef.current?.files?.[0] ?? null;

    if (!selectedFile) {
      setError("Please choose a PDF, DOCX, or TXT file first.");
      return;
    }

    if (status === "working") return;
    setError("");
    setStatus("working");
    setPhase(0);

    let timer: ReturnType<typeof setInterval> | undefined;
    timer = setInterval(() => {
      setPhase((current) => Math.min(current + 1, phases.length - 1));
    }, 1800);

    try {
      const body = new FormData();
      body.append("file", selectedFile);
      body.append("theme_override", theme);

      const response = await fetch(`${API_URL}/presentations/generate`, {
        method: "POST",
        body,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail ?? "Presentation generation failed.");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const name = parseFilename(response.headers.get("content-disposition"));

      setDownloadUrl((old) => {
        if (old) URL.revokeObjectURL(old);
        return url;
      });
      setDownloadName(name);
      setResultMeta({
        theme: response.headers.get("x-slidepilot-theme") ?? undefined,
        slides: response.headers.get("x-slidepilot-slides") ?? undefined,
      });
      setPhase(phases.length - 1);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      if (timer) clearInterval(timer);
    }
  }

  function download() {
    if (!downloadUrl) return;
    const anchor = document.createElement("a");
    anchor.href = downloadUrl;
    anchor.download = downloadName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  }

  return (
    <main className="shell">
      <div className="ambient ambientOne" />
      <div className="ambient ambientTwo" />
      <div className="gridGlow" />

      <header className="topbar">
        <a className="brand" href="#top" aria-label="SlidePilot home">
          <span className="logoMark"><i /><i /><i /></span>
          <span>SlidePilot</span>
        </a>
        <div className="topPill"><span className="liveDot" /> Local workspace</div>
      </header>

      <section id="top" className="hero">
        <div className="eyebrow">AI PRESENTATION WORKFLOW</div>
        <h1>Turn documents into<br /><span>professional presentations.</span></h1>
        <p className="heroCopy">
          Upload a PDF, Word document, or text file. SlidePilot understands the content,
          chooses a presentation structure, applies a theme, and exports an editable PPTX.
        </p>

        <div className="workspace">
          <div className="workspaceHeader">
            <div>
              <span className="stepLabel">01 / DOCUMENT</span>
              <h2>Start with your source</h2>
            </div>
            <div className="fileTypes"><span>PDF</span><span>DOCX</span><span>TXT</span></div>
          </div>

          <div
            className={`dropzone ${file ? "hasFile" : ""}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            <input
              ref={inputRef}
              id="source-file"
              type="file"
              accept=".pdf,.docx,.txt"
              className="fileInput"
              aria-label="Choose source document"
              onChange={(e) => {
                const selectedFile = e.currentTarget.files?.[0] ?? null;
                chooseFile(selectedFile);
              }}
            />

            <div className="uploadIcon">
              {file ? <span className="check">✓</span> : <span className="arrow">↑</span>}
            </div>

            {file ? (
              <>
                <strong>{file.name}</strong>
                <span>{(file.size / 1024 / 1024).toFixed(2)} MB · click to replace</span>
              </>
            ) : (
              <>
                <strong>Drop your document here</strong>
                <span>or click to browse · maximum 20 MB</span>
              </>
            )}
          </div>

          <div className="optionsGrid singleOption">
            <div className="optionBlock">
              <label htmlFor="theme">Presentation style</label>
              <select id="theme" value={theme} onChange={(e) => setTheme(e.target.value as ThemeChoice)}>
                <option value="auto">Auto — let SlidePilot decide</option>
                <option value="technology">Technology</option>
                <option value="business">Business</option>
                <option value="academic">Academic</option>
              </select>
            </div>
            <div className="visualAutoNote">
              <strong>Visual intelligence is automatic</strong>
              <span>SlidePilot chooses images, diagrams, charts, tables, timelines, or workflows based on the content.</span>
            </div>
          </div>

          {status === "working" && (
            <div className="progressPanel">
              <div className="progressTop">
                <span>Generating presentation</span>
                <span>{Math.round(((phase + 1) / phases.length) * 100)}%</span>
              </div>
              <div className="progressTrack"><div style={{ width: `${((phase + 1) / phases.length) * 100}%` }} /></div>
              <div className="phaseList">
                {phases.map((item, index) => (
                  <span key={item} className={index <= phase ? "active" : ""}>
                    <i>{index < phase ? "✓" : index + 1}</i>{item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {status === "ready" && (
            <div className="readyPanel">
              <div className="readyIcon">✓</div>
              <div>
                <span className="stepLabel">PRESENTATION READY</span>
                <h3>{downloadName}</h3>
                <p>{resultMeta.slides ? `${resultMeta.slides} slides` : "PPTX generated"}{resultMeta.theme ? ` · ${resultMeta.theme} theme` : ""}</p>
              </div>
              <button className="downloadButton" onClick={download}>Download PPTX <span>↓</span></button>
            </div>
          )}

          {error && <div className="errorPanel">{error}</div>}

          <button className="generateButton" disabled={status === "working"} onClick={generate}>
            {status === "working" ? "SlidePilot is working…" : "Generate presentation"}
            <span>→</span>
          </button>
        </div>

        <div className="featureRow">
          <div><strong>Structured AI planning</strong><span>10 slide layouts selected from the document itself.</span></div>
          <div><strong>Theme intelligence</strong><span>Technology, business, and academic design languages.</span></div>
          <div><strong>Editable PowerPoint</strong><span>Charts, tables, text, and shapes remain editable in PPTX.</span></div>
        </div>
      </section>

      <footer>
        <span>SlidePilot</span>
        <span>Document → Intelligence → Presentation</span>
      </footer>
    </main>
  );
}
