import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename

from src.supabase_client import supabase, supabase_admin
from src.asr_vosk import speech_to_text
from src.intent_classifier import detect_intent
from src.tts import speak
from src.medical_chatbot import medical_chatbot_response

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------
# AUTH ROUTES
# ---------------------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        try:
            result = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            user_id = result.user.id

            # create profile (uses admin client)
            supabase_admin.table("profiles").insert({
                "id": user_id,
                "name": name
            }).execute()

            return redirect(url_for("login"))

        except Exception as e:
            return f"Registration error: {e}"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session["user_id"] = result.user.id
            session["user_email"] = result.user.email

            return redirect(url_for("dashboard"))

        except Exception as e:
            return f"Login error: {e}"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------
# DASHBOARD
# ---------------------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    profile = supabase_admin.table("profiles") \
        .select("name") \
        .eq("id", session["user_id"]) \
        .execute()

    name = profile.data[0]["name"] if profile.data else "User"

    return render_template("dashboard.html", name=name)


# ---------------------------
# ASSISTANT (VOICE)
# ---------------------------

@app.route("/assistant")
def assistant():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("assistant.html")


@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"})

    audio = request.files["audio"]
    webm_path = os.path.join(UPLOAD_FOLDER, "voice.webm")
    wav_path = os.path.join(UPLOAD_FOLDER, "voice.wav")

    audio.save(webm_path)

    # Convert to WAV (ffmpeg required)
    os.system(f'ffmpeg -y -i "{webm_path}" -ac 1 -ar 16000 "{wav_path}"')

    text = speech_to_text(wav_path)
    intent = detect_intent(text)

    # STORE VOICE HISTORY (ADMIN CLIENT)
    supabase_admin.table("voice_history").insert({
        "user_id": session["user_id"],
        "text": text,
        "intent": intent
    }).execute()

    # Voice reply
    speak(text)

    return jsonify({
        "text": text,
        "intent": intent
    })


# ---------------------------
# CHATBOT
# ---------------------------

@app.route("/chatbot")
def chatbot():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("chatbot.html")


@app.route("/chatbot_api", methods=["POST"])
def chatbot_api():
    if "user_id" not in session:
        return jsonify({"reply": "Session expired. Please login again."}), 401

    data = request.get_json()
    user_message = data.get("message", "")

    reply = medical_chatbot_response(user_message)

    # Save history
    supabase_admin.table("chatbot_history").insert({
        "user_id": session["user_id"],
        "user_message": user_message,
        "bot_reply": reply
    }).execute()

    # TTS should NEVER block response
    try:
        speak(reply)
    except Exception as e:
        print("TTS failed:", e)

    return jsonify({"reply": reply})


# ---------------------------
# REPORTS
# ---------------------------

@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("login"))

    voice_logs = supabase_admin.table("voice_history") \
        .select("*") \
        .eq("user_id", session["user_id"]) \
        .order("created_at", desc=True) \
        .execute().data

    chatbot_logs = supabase_admin.table("chatbot_history") \
        .select("*") \
        .eq("user_id", session["user_id"]) \
        .order("created_at", desc=True) \
        .execute().data

    return render_template(
        "reports.html",
        voice_logs=voice_logs,
        chatbot_logs=chatbot_logs
    )


# ---------------------------
# RUN
# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)