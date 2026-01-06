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
from src.medical_chatbot import medical_chatbot_response


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


# ==================== AUTH ====================
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


# ==================== PAGES ====================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", name=session["user_name"])


@app.route("/")
def home():
    return redirect(url_for("assistant"))


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


# ==================== CHATBOT API ====================
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    reply = medical_chatbot_response(data["message"])
    speak(reply)
    return jsonify({"reply": reply})


# ==================== INIT DB ====================
with app.app_context():
    db.create_all()


# ==================== RUN ====================
if __name__ == "__main__":
    app.run(debug=True)