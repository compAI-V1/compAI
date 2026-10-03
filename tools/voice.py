from __future__ import annotations
import os
from pathlib import Path
import httpx

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "files"

def synthesize_speech(text: str, filename: str = "response.mp3") -> str:
    key = os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY is not configured")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    response = httpx.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": key, "Accept": "audio/mpeg", "Content-Type": "application/json"},
        json={"text": text, "model_id": os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")},
        timeout=60,
    )
    response.raise_for_status()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = Path(filename).name if filename else "response.mp3"
    if not safe_name.endswith(".mp3"): safe_name += ".mp3"
    path = OUTPUT_DIR / safe_name
    path.write_bytes(response.content)
    return str(path)
