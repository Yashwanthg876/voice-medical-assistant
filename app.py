# ==================== IMPORTS ====================
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

from src.asr_vosk import speech_to_text
from src.intent import detect_intent
from src.image_model import predict_disease
from src.tts import speak


# ==================== APP SETUP ====================
app = Flask(__name__)
app.secret_key = "super_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


# ==================== DATABASE MODELS ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))


class VoiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    text = db.Column(db.String(500))
    intent = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ImageHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    prediction = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== EMERGENCY HANDLER ====================
def handle_emergency(text):
    print("🚨 EMERGENCY ALERT TRIGGERED 🚨")
    speak("Emergency detected. Alert has been sent to caregiver and hospital.")
    return "ALERT_SENT"


# ==================== AUTH ROUTES ====================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("dashboard"))
        return "Invalid credentials"
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== DASHBOARD ====================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["user_name"])


# ==================== ASSISTANT ====================
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("assistant"))


@app.route("/assistant")
def assistant():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("assistant.html")


# ==================== VOICE API ====================
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"})

    audio = request.files["audio"]
    webm = os.path.join(UPLOAD_FOLDER, "voice.webm")
    wav = os.path.join(UPLOAD_FOLDER, "voice.wav")

    audio.save(webm)
    os.system(f'ffmpeg -y -i "{webm}" -ac 1 -ar 16000 -acodec pcm_s16le "{wav}"')

    text = speech_to_text(wav)
    intent = detect_intent(text)

    history = VoiceHistory(
        user_id=session["user_id"],
        text=text,
        intent=intent
    )
    db.session.add(history)
    db.session.commit()

    if intent == "EMERGENCY":
        handle_emergency(text)
        return jsonify({"text": text, "intent": intent, "alert": "SENT"})

    speak(f"You said {text}. Detected intent {intent}.")
    return jsonify({"text": text, "intent": intent})


# ==================== IMAGE API ====================
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"})

    image = request.files["image"]
    path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(path)

    result = predict_disease(path)

    history = ImageHistory(
        user_id=session["user_id"],
        prediction=result["prediction"],
        confidence=result["confidence"]
    )
    db.session.add(history)
    db.session.commit()

    return jsonify(result)


# ==================== REPORTS ====================
@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("login"))

    voice_logs = VoiceHistory.query.filter_by(user_id=session["user_id"]).all()
    image_logs = ImageHistory.query.filter_by(user_id=session["user_id"]).all()

    return render_template(
        "reports.html",
        voice_logs=voice_logs,
        image_logs=image_logs
    )


# ==================== INIT DB ====================
with app.app_context():
    db.create_all()


# ==================== RUN ====================
if __name__ == "__main__":
    app.run(debug=True)