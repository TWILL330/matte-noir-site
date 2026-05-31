# Matte Noir — Narration Studio

A Flask + ElevenLabs text-to-speech web app with a dark-themed UI.

## Setup

### 1. Clone & install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `ELEVENLABS_API_KEY` | Your ElevenLabs API key (found in your account settings) |
| `VOICE_ID` | The ElevenLabs voice ID to use (e.g. `21m00Tcm4TlvDq8ikWAM` for Rachel) |

Then export them before running:

```bash
export $(cat .env | xargs)
```

Or set them inline:

```bash
ELEVENLABS_API_KEY=xxx VOICE_ID=yyy python app.py
```

### 3. Run the app

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Usage

1. Paste your narration script into the text area.
2. Adjust **Stability**, **Similarity**, and **Style** sliders as needed.
3. Click **Generate Narration** — the audio plays automatically when ready.
4. Use **Download MP3** to save the file locally.
5. The **Generation History** panel shows previous scripts; click **Replay** to re-play any of them.

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/generate` | Accepts `{ text, stability, similarity, style }`, returns MP3 audio |
| `GET` | `/history` | Returns JSON list of all generated narrations (in-memory, resets on restart) |

## Finding Voice IDs

Browse available voices at the ElevenLabs voice library or use the API:

```bash
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/voices
```
