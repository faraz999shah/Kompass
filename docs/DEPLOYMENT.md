# Running and hosting the API

## Configuration

The API reads its settings (`api/app/config.py`) from the environment, or from `api/.env` when started inside `api/`. Copy `.env.example` from the repo root to get every option with a comment. Keys stay on the server and never go in git.

| Variable | Needed for | Default |
|---|---|---|
| `LLM_API_KEY`, `LLM_MODEL` | Lesson wording, translation, Ask Kiko lessons | unset: English templates only |
| `GEMINI_API_KEY` | Speech-to-text and server read-aloud | unset: voice endpoints return `503 speech_unavailable` |
| `VOICE_MAX_AUDIO_BYTES` | Recording upload limit | 5 MB |
| `VOICE_REQUESTS_PER_MINUTE` | Speech calls per client per minute | 30 |
| `VOICE_DEV_FIXTURES` | Local testing without a Gemini key | `false`; never enable on a hosted server |
| `CORS_ALLOWED_ORIGINS` | The browser build only; native apps send no Origin | Expo web on port 8081 |
| `DATABASE_PATH` | SQLite file for learners and generated lessons | `kompass.db` |

## Run locally

```bash
cd api
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # add your keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`GET /health` returns `{"status": "ok"}`, and the interactive reference is at `/docs`.

## Point the app at it

Set `EXPO_PUBLIC_API_URL` in `app/.env` and restart Expo. This value is bundled into the app, so it must never hold a key.

| Where the app runs | URL to use |
|---|---|
| Browser or iOS simulator | `http://localhost:8000` |
| Android emulator | `http://10.0.2.2:8000` |
| Phone with Expo Go | Your computer's LAN address, e.g. `http://192.168.1.23:8000`, on the same Wi-Fi |

Some guest networks block traffic between devices. If so, use a phone hotspot or a hosted URL. `expo start --tunnel` only tunnels the JavaScript bundle, not the API.

## Host it

The API is a single Python web process, so any service that runs one works:

- **Build:** `pip install -r requirements.txt` (root directory `api`, Python 3.11)
- **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check:** `/health`
- **Secrets:** the variables above, entered in the host's secret settings

Two things to know:

- Free tiers usually have a temporary disk, so the SQLite file resets on each deploy. Attach a persistent disk and point `DATABASE_PATH` at it to keep learners.
- The voice rate limit is kept in memory, so it applies per instance. Run one instance, or move the counts to a shared store before scaling out.
