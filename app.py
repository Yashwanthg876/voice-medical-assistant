# -------------------- IMPORTS --------------------
from flask import Flask, request, jsonify, render_template
import os
from src.asr_vosk import speech_to_text

# -------------------- FLASK APP --------------------
app = Flask(__name__)

# -------------------- CONFIG --------------------
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# -------------------- ROUTES --------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    try:
        if "audio" not in request.files:
            return jsonify({"text": "No audio received"})

        audio = request.files["audio"]

        webm_path = os.path.join(UPLOAD_FOLDER, "voice.webm")
        wav_path = os.path.join(UPLOAD_FOLDER, "voice.wav")

        audio.save(webm_path)

        # Convert webm → wav using ffmpeg
        cmd = (
            f'ffmpeg -y -i "{webm_path}" '
            f'-ac 1 -ar 16000 -acodec pcm_s16le "{wav_path}"'
        )
        os.system(cmd)

        if not os.path.exists(wav_path):
            return jsonify({"text": "Audio conversion failed"})

        text = speech_to_text(wav_path)

        return jsonify({"text": text if text else "No speech detected"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"text": "Server error"})


# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    app.run(debug=True)