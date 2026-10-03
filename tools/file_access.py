from __future__ import annotations
import os, shutil, tempfile
from pathlib import Path

def _find_root():
    cand = Path(os.getenv("FILES_ROOT", "./data/files")).resolve()
    try:
        cand.mkdir(parents=True, exist_ok=True)
        probe = cand / ".probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return cand
    except OSError:
        fb = Path(tempfile.gettempdir()) / "compai-files"
        fb.mkdir(parents=True, exist_ok=True)
        return fb

ROOT = _find_root()
ALLOWED = {".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".css", ".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg"}

def safe_path(relative: str) -> Path:
    candidate = (ROOT / relative).resolve()
    if candidate != ROOT and ROOT not in candidate.parents:
        raise ValueError("Path escapes FILES_ROOT")
    if candidate.suffix.lower() not in ALLOWED:
        raise ValueError("File extension is not allowed")
    return candidate

def list_files():
    return [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and not p.name.endswith(".bak")]

def read_file(path: str):
    target = safe_path(path)
    return target.read_text(encoding="utf-8")

def write_file(path: str, content: str):
    target = safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists(): shutil.copy2(target, target.with_name(target.name + ".bak"))
    target.write_text(content, encoding="utf-8")
    return str(target.relative_to(ROOT))
