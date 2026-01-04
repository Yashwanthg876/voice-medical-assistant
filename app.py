# ==================== IMPORTS ====================
from flask import Flask, request, jsonify, render_template
import os

from src.asr_vosk import speech_to_text
from src.intent import detect_intent
from src.image_model import predict_disease


# ==================== APP SETUP ====================
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


# ==================== ROUTES ====================

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# -------- VOICE PROCESSING --------
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    try:
        if "audio" not in request.files:
            return jsonify({
                "text": "No audio received",
                "intent": "NONE"
            })

        audio = request.files["audio"]

        webm_path = os.path.join(UPLOAD_FOLDER, "voice.webm")
        wav_path = os.path.join(UPLOAD_FOLDER, "voice.wav")

        # Save uploaded audio
        audio.save(webm_path)

        # Convert webm -> wav using ffmpeg
        cmd = (
            f'ffmpeg -y -i "{webm_path}" '
            f'-ac 1 -ar 16000 -acodec pcm_s16le "{wav_path}"'
        )
        os.system(cmd)

        if not os.path.exists(wav_path):
            return jsonify({
                "text": "Audio conversion failed",
                "intent": "ERROR"
            })

        # Speech to text
        text = speech_to_text(wav_path)

        # Intent detection
        intent = detect_intent(text)

        return jsonify({
            "text": text if text else "No speech detected",
            "intent": intent
        })

    except Exception as e:
        print("VOICE ERROR:", e)
        return jsonify({
            "text": "Server error occurred",
            "intent": "ERROR"
        })


# -------- IMAGE PROCESSING --------
@app.route("/upload_image", methods=["POST"])
def upload_image():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"})

        image = request.files["image"]
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

        # AI image prediction
        result = predict_disease(image_path)

        return jsonify({
            "prediction": result["prediction"],
            "confidence": result["confidence"]
        })

    except Exception as e:
        print("IMAGE ERROR:", e)
        return jsonify({"error": "Image processing failed"})


# ==================== RUN SERVER ====================
if __name__ == "__main__":
    app.run(debug=True)