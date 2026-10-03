from __future__ import annotations
import os

APP_ENV = os.getenv("APP_ENV", "development").lower()
IS_PRODUCTION = APP_ENV in {"prod", "production"}
TOKEN_SECRET = os.getenv("APP_TOKEN_SECRET", "dev-only-change-me")
DEMO_MODE = os.getenv("COMPAI_DEMO", "1") == "1"

def validate_config():
    if IS_PRODUCTION:
        if TOKEN_SECRET == "dev-only-change-me" or len(TOKEN_SECRET) < 32:
            if not DEMO_MODE: raise RuntimeError("APP_TOKEN_SECRET must be a random value of at least 32 characters in production")
        if not os.getenv("ANTHROPIC_API_KEY") and not DEMO_MODE: raise RuntimeError("ANTHROPIC_API_KEY is required in production (set COMPAI_DEMO=1 to run without it)")
        if os.getenv("CODE_EXECUTION_MODE", "local") != "runner" and not DEMO_MODE: raise RuntimeError("Production requires CODE_EXECUTION_MODE=runner (set COMPAI_DEMO=1 to disable code execution)")
    return True

def readiness():
    return {"status":"ready", "environment":APP_ENV, "claude_configured":bool(os.getenv("ANTHROPIC_API_KEY")), "database":"configured", "code_execution_mode":os.getenv("CODE_EXECUTION_MODE", "local")}
