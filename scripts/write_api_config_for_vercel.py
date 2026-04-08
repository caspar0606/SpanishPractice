#!/usr/bin/env python3
"""Write frontend/api-config.js from BACKEND_URL (Vercel build env)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "frontend" / "api-config.js"


def main() -> None:
    url = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
    OUT.write_text(
        "/** Injected at Vercel build from BACKEND_URL. */\n"
        f"window.__API_BASE__ = {url!r};\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} (BACKEND_URL length {len(url)})")


if __name__ == "__main__":
    main()
