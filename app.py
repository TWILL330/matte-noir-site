import os
import io
import re
import base64
import tempfile
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


def chars_to_words(characters, char_start_times, char_end_times):
    """Convert character-level ElevenLabs alignment to word-level timing."""
    words = []
    word_start = None
    word_chars = []
    word_end = None

    for ch, st, et in zip(characters, char_start_times, char_end_times):
        if ch.strip():
            if word_start is None:
                word_start = st
            word_chars.append(ch)
            word_end = et
        else:
            if word_chars:
                words.append({"word": "".join(word_chars), "start": word_start, "end": word_end})
                word_chars = []
                word_start = None
                word_end = None

    if word_chars:
        words.append({"word": "".join(word_chars), "start": word_start, "end": word_end})

    return words


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/voices", methods=["GET"])
def voices():
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ELEVENLABS_API_KEY not set"}), 503
    try:
        resp = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=15,
        )
        if resp.status_code != 200:
            return jsonify({"error": f"ElevenLabs error {resp.status_code}"}), 502
        data = resp.json()
        result = []
        for v in data.get("voices", []):
            labels = v.get("labels", {})
            result.append({
                "voice_id": v["voice_id"],
                "name": v["name"],
                "language": labels.get("language", labels.get("accent", "")),
                "gender": labels.get("gender", ""),
                "category": v.get("category", ""),
            })
        result.sort(key=lambda v: v["name"].lower())
        return jsonify({"voices": result, "default": VOICE_ID})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

    elif ext == ".epub":
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup

            content = f.read()
            with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                book = epub.read_epub(tmp_path)
                chapters = []
                for item in book.get_items():
                    if item.get_type() == ebooklib.ITEM_DOCUMENT:
                        soup = BeautifulSoup(item.get_content(), "html.parser")
                        chapters.append(soup.get_text(separator="\n"))
                text = "\n\n".join(chapters).strip()
            finally:
                os.unlink(tmp_path)

            if not text:
                return jsonify({"error": "No text found in this ePub"}), 422
            _document_text = text
            return jsonify({"text": text})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif ext == ".docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(f.read()))
            text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            if not text:
                return jsonify({"error": "No text found in this document"}), 422
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
        return jsonify({"error": f"Unsupported file type '{ext}'. Upload a PDF, ePub, .docx, or image."}), 400


@app.route("/fetch-url", methods=["POST"])
def fetch_url():
    global _document_text
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "url is required"}), 400

    try:
        from bs4 import BeautifulSoup
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MatteNoir/1.0)"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        article = (soup.find("article") or soup.find(id="content") or
                   soup.find(class_="content") or soup.find("main") or soup.body)
        raw = article.get_text(separator="\n") if article else soup.get_text(separator="\n")
        lines = [l.strip() for l in raw.split("\n")]
        text = "\n".join(l for l in lines if l)
        if not text:
            return jsonify({"error": "No readable text found at URL"}), 422
        _document_text = text
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        return jsonify({"text": text, "title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate", methods=["POST"])
def generate():
    global _document_text
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    voice_id = data.get("voice_id", "") or VOICE_ID
    if not voice_id:
        return jsonify({"error": "No voice selected. Choose a voice or set VOICE_ID env var."}), 400

    if data.get("natural", True):
        text = prepare_for_narration(text)

    _document_text = _document_text or text

    stability = float(data.get("stability", 0.5))
    similarity = float(data.get("similarity", 0.75))
    style = float(data.get("style", 0.3))
    with_timestamps = bool(data.get("with_timestamps", False))

    el_headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
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

    if with_timestamps:
        el_headers["Accept"] = "application/json"
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
            headers=el_headers, json=payload, timeout=60,
        )
        if resp.status_code != 200:
            return jsonify({"error": f"ElevenLabs error {resp.status_code}: {resp.text}"}), 502

        result = resp.json()
        alignment = result.get("alignment", {})
        words = chars_to_words(
            alignment.get("characters", []),
            alignment.get("character_start_times_seconds", []),
            alignment.get("character_end_times_seconds", []),
        )
        _history.append({
            "text": data.get("text", "")[:120],
            "stability": stability, "similarity": similarity, "style": style,
        })
        return jsonify({"audio": result.get("audio_base64", ""), "words": words})

    else:
        el_headers["Accept"] = "audio/mpeg"
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers=el_headers, json=payload, timeout=60,
        )
        if resp.status_code != 200:
            return jsonify({"error": f"ElevenLabs error {resp.status_code}: {resp.text}"}), 502

        _history.append({
            "text": data.get("text", "")[:120],
            "stability": stability, "similarity": similarity, "style": style,
        })
        buf = io.BytesIO(resp.content)
        buf.seek(0)
        return send_file(buf, mimetype="audio/mpeg", as_attachment=False, download_name="narration.mp3")


@app.route("/podcast", methods=["POST"])
def podcast():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    notes = data.get("notes", "").strip()
    if not prompt and not notes:
        return jsonify({"error": "prompt or notes required"}), 400

    client = anthropic_client()
    if not client:
        return jsonify({"error": "Set ANTHROPIC_API_KEY for podcast generation"}), 503

    try:
        context = (f"Topic: {prompt}\n\n" if prompt else "") + (f"Source notes:\n{notes[:20000]}" if notes else "")
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=(
                "You are a podcast script writer. Write engaging, conversational podcast narration. "
                "Use a warm, direct tone speaking to the audience as a single host. "
                "Include a natural intro, key points with examples, and a closing summary. "
                "Plain paragraphs only — no markdown, no headers, no stage directions. "
                "Aim for 450-750 words (3-5 minutes when read aloud)."
            ),
            messages=[{"role": "user", "content": context}],
        )
        return jsonify({"script": msg.content[0].text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/clone-voice", methods=["POST"])
def clone_voice():
    if not ELEVENLABS_API_KEY:
        return jsonify({"error": "ELEVENLABS_API_KEY not set"}), 503

    name = request.form.get("name", "My Cloned Voice")
    uploaded = request.files.getlist("audio")
    if not uploaded:
        return jsonify({"error": "No audio files uploaded"}), 400

    try:
        audio_files = [
            ("files", (f.filename, f.read(), f.content_type or "audio/mpeg"))
            for f in uploaded
        ]
        resp = requests.post(
            "https://api.elevenlabs.io/v1/voices/add",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            data={"name": name},
            files=audio_files,
            timeout=60,
        )
        if resp.status_code not in (200, 201):
            return jsonify({"error": f"ElevenLabs error {resp.status_code}: {resp.text}"}), 502
        result = resp.json()
        return jsonify({"voice_id": result.get("voice_id"), "name": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    app.run(debug=True, host="0.0.0.0", port=8080)
