# ==================== IMPORTS ====================
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

from src.medical_chatbot import medical_chatbot_response
from src.tts import speak


# ==================== APP SETUP ====================
app = Flask(__name__)
app.secret_key = "super_secret_key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==================== DATABASE MODEL ====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))


# ==================== AUTH ====================
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


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", name=session.get("user_name"))


# ==================== CHATBOT PAGES ====================
@app.route("/")
def home():
    return redirect(url_for("chatbot_page"))


@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


# ==================== CHATBOT API (FIXED) ====================
@app.route("/chatbot_api", methods=["POST"])
def chatbot_api():
    data = request.get_json()

    user_message = data.get("message", "")
    reply = medical_chatbot_response(user_message)

    # Voice feedback
    speak(reply)

    return jsonify({
        "reply": reply
    })


# ==================== INIT DB ====================
with app.app_context():
    db.create_all()


# ==================== RUN ====================
if __name__ == "__main__":
    app.run(debug=True)