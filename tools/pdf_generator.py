from __future__ import annotations
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "data" / "files"

def generate_pdf(title: str, subtitle: str | None = None, sections: list[dict] | None = None, sources: list[dict] | None = None) -> dict:
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise RuntimeError("WeasyPrint is not installed or its system libraries are unavailable") from exc
    OUT.mkdir(parents=True, exist_ok=True)
    html = Environment(loader=FileSystemLoader(BASE / "templates")).get_template("report.html").render(title=title, subtitle=subtitle, sections=sections or [], sources=sources or [])
    path = OUT / "report.pdf"
    HTML(string=html, base_url=str(BASE)).write_pdf(str(path))
    return {"path": str(path)}
