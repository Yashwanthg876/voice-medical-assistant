# ==================== IMPORTS ====================
from flask import Flask, request, jsonify, render_template
import os

from src.asr_vosk import speech_to_text
from src.intent import detect_intent
from src.image_model import predict_disease
from src.tts import speak


# ==================== APP SETUP ====================
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


# ==================== EMERGENCY HANDLER ====================
def handle_emergency(text):
    print("🚨 EMERGENCY ALERT TRIGGERED 🚨")
    print("User message:", text)
    print("Notifying caregiver / hospital (SIMULATED)")

    return {
        "status": "ALERT_SENT",
        "message": "Emergency alert sent to caregiver and hospital"
    }


# ==================== ROUTES ====================

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

        # Save audio
        audio.save(webm_path)

        # Convert to WAV
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

        # Speech → Text
        text = speech_to_text(wav_path)

        # Intent Detection
        intent = detect_intent(text)

        # Emergency Handling
        if intent == "EMERGENCY":
            alert = handle_emergency(text)
            speak("Emergency detected. Alert has been sent to caregiver and hospital.")

            return jsonify({
                "text": text,
                "intent": intent,
                "alert_status": alert["status"],
                "alert_message": alert["message"]
            })

        # Normal Voice Feedback
        response_text = f"You said {text}. Detected intent is {intent}."
        speak(response_text)

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