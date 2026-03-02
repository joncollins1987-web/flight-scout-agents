# flight-scout-agents

Production-shaped MVP web app that searches flights through a multi-agent pipeline (OpenAI Agents SDK), verifies top candidates in-run, computes true total cost, and returns three tabs: Cheapest, Nonstop, and Strategic.

## Stack
- Frontend: Next.js + TypeScript + Tailwind (`/frontend`)
- Backend: FastAPI + Python + OpenAI Agents SDK + Playwright (`/backend`)
- Storage: SQLite (SQLModel)
- Artifacts: SQLite + `/backend/runs/<run_id>` JSON/log/evidence files
- Local orchestration: `docker-compose`
- Tests: `pytest` with fixture mode (`dry_run=true`)

## Defaults and Assumptions
- Traveler defaults: 1 adult, economy, USD.
- Default NYC origins: `JFK`, `EWR`, `LGA`.
- Nearby airports when enabled: `HPN`, `ISP`, `PHL`.
- Cache TTL: 45 minutes.
- Verify top N per tab defaults to 5 (top 3 minimum policy).
- Material verification price change threshold: 5%.
- If no verified itinerary exists, API returns best unverified with warning status.

## Multi-Agent Design
Agents implemented in `backend/app/agents/` with strict JSON output contracts and SchemaGuard enforcement (one repair retry then hard-fail branch):
1. Planner/Judge Agent
2. Scout_Aggregator_1 Agent
3. Scout_Aggregator_2 Agent
4. Deduper/Normalizer Agent
5. Constraints Lawyer Agent
6. Verifier Agent (Playwright)
7. Strategic Ranker Agent
8. Stopover Itinerary Agent
9. Final Presenter Agent

Explicit handoff graph is declared in:
- `backend/app/agents/handoffs.py`
- `backend/app/agents/factory.py` (SDK handoffs)

## API
### `POST /api/search`
- Input: `SearchRequest`
- Output: `FinalSearchResult`
- Supports `dry_run=true` to force fixture mode (no live source scraping).

### `GET /api/runs/{run_id}`
- Returns persisted run metadata and final result payload.

### Optional `GET /api/runs`
- Lists recent runs for debugging.

## Local Development
### Option A: Docker Compose (one command)
1. Create env file:
   - `cp .env.example .env`
2. Start:
   - `docker compose up --build`
3. Open:
   - Frontend: `http://localhost:3000`
   - Backend docs: `http://localhost:8000/docs`

### Option B: Without Docker
1. Backend setup:
   - `cd backend`
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install --upgrade pip`
   - `pip install -e .[dev]`
   - `python -m playwright install chromium`
   - `uvicorn app.main:app --reload --port 8000`
2. Frontend setup:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## Deploy to Vercel (Frontend)
1. Push this repo to GitHub/GitLab/Bitbucket.
2. In Vercel Dashboard click `Add New...` -> `Project`.
3. Import repository.
4. In `Configure Project`:
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
5. In Environment Variables set:
   - `NEXT_PUBLIC_BACKEND_URL` = your backend URL (Render URL)
6. Click `Deploy`.

## Deploy to Render (Backend)
1. Push this repo to GitHub/GitLab.
2. In Render Dashboard click `New +` -> `Blueprint`.
3. Select repository containing this project.
4. Render detects `render.yaml` in repo root.
5. Confirm service settings:
   - Service Name: `flight-scout-backend`
   - Root Directory: `backend` (from `render.yaml`)
   - Build Command installs dependencies and Playwright Chromium.
   - Start Command runs Gunicorn/Uvicorn worker.
6. Set secret env var before deploy:
   - `OPENAI_API_KEY`
7. Click `Apply`.

## Environment Variables
Required/used variables:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `DATABASE_URL` (default `sqlite:///./data/flight_scout.db`)
- `CACHE_TTL_MINUTES`
- `VERIFY_TOP_N_PER_TAB`
- `VERIFICATION_STALE_MINUTES`
- `SOURCE_AGGREGATOR_ONE_ENABLED`
- `SOURCE_AGGREGATOR_TWO_ENABLED`
- `ENABLE_LIVE_SOURCES`
- `PLAYWRIGHT_HEADLESS`
- `PLAYWRIGHT_TIMEOUT_MS`
- `LOG_LEVEL`
- `NEXT_PUBLIC_BACKEND_URL` (frontend)

## Run Artifacts and Persistence
Per run artifacts are saved to:
- `backend/runs/<run_id>/inputs.json`
- `backend/runs/<run_id>/candidates.json`
- `backend/runs/<run_id>/verified.json`
- `backend/runs/<run_id>/final.json`
- `backend/runs/<run_id>/logs.ndjson`
- `backend/runs/<run_id>/evidence/*` (screenshots when available)

SQLite tables:
- `runs`
- `candidates`
- `verified`
- `final_results`

## Add a New Source Module
1. Create module under `backend/app/sources/<source_name>.py` implementing:
   - `search(request: SearchRequest) -> list[RawItineraryCandidate]`
2. Add config flag wiring in `backend/app/core/config.py`.
3. Register source in orchestrator parallel scout step (`backend/app/agents/orchestrator.py`).
4. Add fixture JSON under `backend/app/tests/fixtures/sources/`.
5. Add fixture-mode tests to ensure source works with `dry_run=true`.

## Testing
From backend root:
- `pytest`

Included tests cover:
- strict schema validation
- SchemaGuard retry/failure behavior
- dedupe/normalization
- strategic scoring
- stopover generation
- source fixture mode
- verifier fixture mode
- API dry-run shape and cache behavior

## Deployment Files
- `vercel.json` (frontend monorepo config; set project root directory to `/frontend` in Vercel)
- `render.yaml` (backend Blueprint with `rootDir: backend`)
- `docker-compose.yml` (local frontend + backend)

## Known Limitations
- Live source scraping is feature-flagged and currently stubbed for safety/reliability.
- Real fare rule extraction is dependent on source page stability and site structure.
- SQLite is suitable for MVP/dev; production should migrate to managed Postgres.
- Verification currently relies on fixture/live simulated extraction patterns, not full OTA checkout automation for every provider.

## Terms, Robots, and Rate Limiting
- Respect each provider's Terms of Service and robots policies before enabling live scraping.
- Keep source rate limits conservative and use cache/TTL to reduce request volume.
- Enable/disable source modules per environment via source flags.
