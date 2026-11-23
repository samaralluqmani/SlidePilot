"use client";

import { type DragEvent, useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const ALLOWED = ["pdf", "docx", "txt"];
const MAX_BYTES = 20 * 1024 * 1024;

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
  const requestRef = useRef(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [downloadName, setDownloadName] = useState("slidepilot_presentation.pptx");
  const [slideCount, setSlideCount] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    };
  }, [downloadUrl]);

  function chooseFile(candidate: File | null) {
    if (!candidate || requestRef.current) return;
    setError("");
    setDownloadUrl(null);
    setFile(null);
    setStatus("idle");

    if (!ALLOWED.includes(fileExtension(candidate.name))) {
      setError("Please choose a PDF, DOCX, or TXT file.");
      return;
    }
    if (!candidate.size) {
      setError("The file is empty.");
      return;
    }
    if (candidate.size > MAX_BYTES) {
      setError("The file is larger than 20 MB.");
      return;
    }

    setFile(candidate);
    void generate(candidate);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    chooseFile(event.dataTransfer.files?.[0] ?? null);
  }

  async function generate(selectedFile: File) {
    if (requestRef.current) return;
    requestRef.current = true;
    setError("");
    setStatus("working");

    try {
      const body = new FormData();
      body.append("file", selectedFile);

      const response = await fetch(`${API_URL}/presentations/generate`, {
        method: "POST",
        body,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail ?? "Presentation generation failed.");
      }

      const blob = await response.blob();
      const name = parseFilename(response.headers.get("content-disposition"));

      setDownloadUrl(URL.createObjectURL(blob));
      setDownloadName(name);
      setSlideCount(response.headers.get("x-slidepilot-slides"));
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      requestRef.current = false;
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
          Upload a PDF, Word document, or text file to generate an editable PowerPoint.
        </p>

        <div className="workspace">
          <div className="workspaceHeader">
            <div>
              <h2>Upload a document</h2>
            </div>
            <div className="fileTypes"><span>PDF</span><span>DOCX</span><span>TXT</span></div>
          </div>

          <div
            className={`dropzone ${file ? "hasFile" : ""}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            <input
              disabled={status === "working"}
              id="source-file"
              type="file"
              accept=".pdf,.docx,.txt"
              className="fileInput"
              aria-label="Choose source document"
              onChange={(e) => {
                const selectedFile = e.currentTarget.files?.[0] ?? null;
                e.currentTarget.value = "";
                chooseFile(selectedFile);
              }}
            />

            <div className="uploadIcon">
              {file ? <span className="check">✓</span> : <span className="arrow">↑</span>}
            </div>

            {file ? (
              <>
                <strong>{file.name}</strong>
                <span>{(file.size / 1024 / 1024).toFixed(2)} MB{status === "working" ? "" : " · click to replace"}</span>
              </>
            ) : (
              <>
                <strong>Drop your document here</strong>
                <span>or click to browse · maximum 20 MB</span>
              </>
            )}
          </div>

          {status === "working" && (
            <div className="progressPanel" role="status">
              <span className="spinner" aria-hidden="true" />
              <div>
                <strong>Generating your presentation</strong>
                <p>Keep this tab open while SlidePilot designs your slides.</p>
              </div>
            </div>
          )}

          {status === "ready" && (
            <div className="readyPanel" role="status">
              <div className="readyIcon">✓</div>
              <div>
                <span className="stepLabel">PRESENTATION READY</span>
                <h3>{downloadName}</h3>
                <p>{slideCount ? `${slideCount} slides` : "PPTX generated"}</p>
              </div>
              <button className="downloadButton" onClick={download}>Download PPTX <span>↓</span></button>
            </div>
          )}

          {error && (
            <div className="errorPanel" role="alert">
              {error}
              {file && status === "error" && (
                <button className="retryButton" onClick={() => void generate(file)}>Try again</button>
              )}
            </div>
          )}
        </div>
      </section>

      <footer>
        <span>SlidePilot</span>
        <span>Document → Intelligence → Presentation</span>
      </footer>
    </main>
  );
}
