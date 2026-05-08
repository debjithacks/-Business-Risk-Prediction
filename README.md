# Business Risk Prediction

This project is a simple **Business Risk Intelligence Dashboard**.

- Backend: FastAPI (Python)
- Frontend: plain HTML/JS (opens in your browser)
- Models: pre-trained `.pkl` files in `models/`

## What it can do

- Predict business risk based on the inputs you enter
- Show graphs and a risk gauge
- Includes chatbot features (AI chat, sentiment, translation, Bengali TTS)

## Project folders

- `api/` — FastAPI backend
- `frontend/` — Dashboard UI (`index.html`)
- `models/` — Saved ML models

## Requirements

- Python 3.10+ (recommended)

Install packages:

```bash
pip install -r requirements.txt
```

## Environment variables (important)

This project uses API keys / database connection strings.
Do **not** hard-code them in code.

1) Copy `.env.example` to `.env`
2) Fill the values

Example:

```bash
# Windows PowerShell
copy .env.example .env
```

Variables used:

- `MONGODB_URI` — MongoDB connection string
- `OPENWEATHER_API_KEY` — OpenWeatherMap key (used by rainfall feature)
- `GROQ_API_KEY` — Groq key (used by chat features)

Notes:

- `.env` is ignored by git (it should not be committed)
- If you do not have these keys yet, you can still use parts of the app that do not need them

## Security changes (what was removed)

For security, these were removed from the code/repo and must be provided locally:

- **MongoDB URI**: removed from code. Set `MONGODB_URI` in your `.env`.
- **OpenWeatherMap key**: removed from code. Set `OPENWEATHER_API_KEY` in your `.env`.
- **Groq key**: do not store in code. Set `GROQ_API_KEY` in your `.env`.

Also, some local/generated files are intentionally not committed:

- `.env` files (secrets)
- Generated outputs like `api/*.pdf` and `api/*.png`
- Local cache/data like `api/bengali_audio_cache/`, `database/user_data.json`, `api/users.json`

If you need these later:

- Ask the project owner/team member for the correct values.
- Add them to your local `.env` (based on `.env.example`).

## Run the backend (API)

From the project root:

```bash
cd api
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API will run at:

- http://127.0.0.1:8000

## Run the frontend (Dashboard)

Open the file:

- `frontend/index.html`

You can also run this command from the `frontend` folder:

```bash
start index.html
```

## Basic usage

1) Start the backend
2) Open the dashboard (`frontend/index.html`)
3) Register or login
4) Fill the form and click **Submit**

## Common problems

- **Backend unreachable**: make sure `uvicorn` is running on port `8000`
- **Missing MONGODB_URI / OPENWEATHER_API_KEY**: create `.env` and set the values
- **Model version warning**: if you see a scikit-learn warning, it usually means the model was trained with a different sklearn version

## Security note

If a secret (API key / MongoDB URI) is accidentally pushed to GitHub:

- Rotate the secret (change password / create new key)
- Remove it from code
- Clean git history if needed

