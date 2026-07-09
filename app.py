import os
import io
import re
import base64
import requests
import anthropic
from flask import Flask, request, jsonify, send_file, render_template
from pypdf import PdfReader

app = Flask(__name__)

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("VOICE_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

_history = []
_document_text = ""

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MEDIA_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
}


def anthropic_client():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def prepare_for_narration(text):
    """Preprocess text so ElevenLabs reads it like a human narrator."""
    lines = text.split("\n")
    out = []
    prev_heading = False

    for line in lines:
        s = line.strip()
        if not s:
            if out and out[-1] not in ("...", ""):
                out.append("")
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)", s)
        is_heading = False
        if heading_match:
            s = heading_match.group(2).strip()
            is_heading = True
        elif len(s) <= 70 and s.isupper() and len(s.split()) >= 2:
            is_heading = True

        if is_heading:
            if out:
                out.append("...")
            out.append(s + ".")
            out.append("...")
            prev_heading = True
        else:
            if prev_heading:
                out.append("...")
            if s[-1] not in ".!?;:":
                s += "."
            out.append(s)
            prev_heading = False

    cleaned = []
    for i, chunk in enumerate(out):
        if chunk == "..." and i > 0 and out[i - 1] == "...":
            continue
        cleaned.append(chunk)

    return " ".join(c for c in cleaned if c)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():
    global _document_text
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    ext = os.path.splitext(f.filename.lower())[1]

    if ext == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(f.read()))
            text = "\n\n".join(p.extract_text() or "" for p in reader.pages).strip()
            if not text:
                return jsonify({"error": "No text found in this PDF"}), 422
            _document_text = text
            return jsonify({"text": text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif ext in IMAGE_EXTS:
        client = anthropic_client()
        if not client:
            return jsonify({"error": "Set ANTHROPIC_API_KEY to extract text from images"}), 503
        try:
            data = base64.standard_b64encode(f.read()).decode()
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {
                            "type": "base64",
                            "media_type": MEDIA_TYPES.get(ext, "image/jpeg"),
                            "data": data,
                        }},
                        {"type": "text", "text": (
                            "Extract all text from this image exactly as it appears. "
                            "Preserve headings, paragraphs, and lists. "
                            "Return only the text, no commentary."
                        )},
                    ],
                }],
            )
            text = msg.content[0].text.strip()
            _document_text = text
            return jsonify({"text": text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": f"Unsupported file type '{ext}'. Upload a PDF or image."}), 400


@app.route("/generate", methods=["POST"])
def generate():
    global _document_text
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    if data.get("natural", True):
        text = prepare_for_narration(text)

    _document_text = _document_text or text

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

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        return jsonify({"error": f"ElevenLabs error {resp.status_code}: {resp.text}"}), 502

    _history.append({
        "text": data.get("text", "")[:120],
        "stability": stability,
        "similarity": similarity,
        "style": style,
    })

    buf = io.BytesIO(resp.content)
    buf.seek(0)
    return send_file(buf, mimetype="audio/mpeg", as_attachment=False, download_name="narration.mp3")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    doc = data.get("text", _document_text).strip()

    if not question:
        return jsonify({"error": "question is required"}), 400
    if not doc:
        return jsonify({"error": "No document loaded — upload a file or paste text first"}), 400

    client = anthropic_client()
    if not client:
        return jsonify({"error": "Set ANTHROPIC_API_KEY to enable Q&A"}), 503

    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=(
                "You are a helpful reading assistant. Answer questions based solely on "
                "the provided document. Be concise. If the answer is not in the document, say so."
            ),
            messages=[{
                "role": "user",
                "content": f"Document:\n\n{doc[:50000]}\n\n---\n\nQuestion: {question}",
            }],
        )
        return jsonify({"answer": msg.content[0].text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def history():
    return jsonify(_history)


if __name__ == "__main__":
    app.run(debug=True)
