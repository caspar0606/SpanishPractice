# Spanish Practice

FastAPI backend plus a small web UI for Spanish **writing**, **reading**, and **drills** practice. Exercises are generated and marked with an LLM (OpenAI via LangChain).

## Features

- **Web UI** at `/` (static assets under `/static/…`) — log in with a shared access code, pick an exercise, generate prompts, submit answers, view feedback.
- **REST API** — same flows; OpenAPI docs at `/docs`, health at `/health`.
- **Per-user JSON storage** under `userdata/<username>.json` (progress, history, current exercise).

## Requirements

- **Python 3.11+** (3.12 works)
- An **OpenAI API key** and LangChain-compatible model configuration (see `src/infrastructure/llm/harness.py`).

## Setup

1. Clone the repo and create a virtual environment (recommended):

   ```bash
   cd SpanishPractice
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy environment variables — create a **`.env`** file in the project root (it is gitignored). At minimum:

   | Variable | Purpose |
   |----------|---------|
   | `OPENAI_API_KEY` | OpenAI API access for the LLM |
   | `ACCESS_KEY` | Shared secret users enter at login (small group) |
   | `CORS_ORIGINS` | Optional, comma-separated origins (e.g. `https://your-app.vercel.app`) when the UI is hosted separately |

   The app loads `.env` from the project root on startup (`src/api/main.py`).

3. Ensure **`userdata/`** exists (it is created when the first user is registered). Add `userdata/` to backups if you care about progress data.

## Run locally

From the **project root** (directory that contains `src/`):

```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Then open:

- **App:** http://127.0.0.1:8000/
- **API docs:** http://127.0.0.1:8000/docs
- **Health:** http://127.0.0.1:8000/health

### Typical user flow (UI)

1. **Log in** — username, `ACCESS_KEY`, optional “new user” on first visit.
2. **Choose exercise** — type (writing / reading / drills), difficulty, weaknesses vs preferences.
3. **Practice** — generate prompt, then submit; optional **My progress** for scores.

## Share over the internet (optional)

For a **no-domain** test link, with the app running on port 8000, use [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) quick mode in a **second** terminal:

```bash
cloudflared tunnel --url http://localhost:8000
```

Use the printed `https://….trycloudflare.com` URL. Keep **both** `uvicorn` and `cloudflared` running. The hostname changes each time you restart the quick tunnel unless you configure a named tunnel and your own domain.

**Security:** The public URL can be discovered; treat `ACCESS_KEY` as the gate and avoid committing secrets.

## Deploy the frontend on Vercel (API elsewhere)

The UI is static files under `frontend/`. By default `api-config.js` keeps an empty API base so requests stay **same-origin** when you use FastAPI to serve `/` and `/static/…`.

To host the UI on **Vercel** and keep the API on another host (Railway, Fly, your VPS, Cloudflare Tunnel URL, etc.):

1. **Backend:** Run the FastAPI app with a public HTTPS URL. Set **`CORS_ORIGINS`** in the API’s environment to your Vercel site origin, e.g. `https://spanish-practice.vercel.app` (no trailing slash). Redeploy or restart the API after changing env vars.

2. **Vercel project:** Point the project at this repo. In **Project → Settings → General**, set **Root Directory** to the repository root (leave it **empty** or `.` — **not** `src` or `frontend`). The included **`vercel.json`** runs `node scripts/write-api-config.mjs`, which writes `frontend/static/api-config.js` from **`BACKEND_URL`**.

3. **Vercel environment variable:** Add **`BACKEND_URL`** = your API origin only, e.g. `https://api.example.com` (no trailing slash). The build step injects it into `api-config.js` so `fetch` calls go to that host.

4. Deploy. Open the Vercel URL; login and API calls should hit your backend. If the browser blocks requests, confirm `CORS_ORIGINS` matches the exact Vercel origin (scheme + host, no path).

Local development unchanged: run uvicorn as before; `api-config.js` stays empty unless you edit it for testing cross-origin.

## Project layout (high level)

```
src/
  api/           # FastAPI app, routers, Pydantic schemas
  application/   # Use cases (user, exercise selection, services)
  domain/        # Models, rules, enums
  infrastructure/# LLM harness, persistence (JSON), config
frontend/        # Static UI: index.html; assets in frontend/static/ (URL /static/…)
userdata/        # Runtime user JSON files (gitignored by default)
```

CLI entrypoints under `src/app/` and related `infrastructure/cli/` are legacy / local use; the primary surface for learners is the **web UI** and **API**.

## Development notes

- **Port in use:** If `8000` is busy, pick another port (e.g. `--port 8001`) and point `cloudflared` at that URL.
- **Dependencies:** `langgraph` / `langchain` versions are pinned in `requirements.txt` for resolver compatibility; use `pip install -r requirements.txt` on a clean env if you see conflicts.
