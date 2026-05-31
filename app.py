import os
import io
import requests
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("VOICE_ID", "")

_history = []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    stability = float(data.get("stability", 0.5))
    similarity = float(data.get("similarity", 0.75))
    style = float(data.get("style", 0.3))

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style,
            "use_speaker_boost": True,
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        return jsonify({"error": f"ElevenLabs error {response.status_code}: {response.text}"}), 502

    _history.append({"text": text, "stability": stability, "similarity": similarity, "style": style})

    audio_bytes = io.BytesIO(response.content)
    audio_bytes.seek(0)
    return send_file(
        audio_bytes,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="narration.mp3",
    )


@app.route("/history", methods=["GET"])
def history():
    return jsonify(_history)


if __name__ == "__main__":
    app.run(debug=True)
