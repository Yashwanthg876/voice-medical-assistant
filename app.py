# ==================== IMPORTS ====================
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from src.supabase_client import supabase
from src.medical_chatbot import medical_chatbot_response
from src.tts import speak


# ==================== APP SETUP ====================
app = Flask(__name__)
app.secret_key = "super_secret_key"


# ==================== AUTH HELPERS ====================
def login_required():
    return "user_id" in session


# ==================== AUTH ROUTES ====================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session["user_id"] = result.user.id
            session["user_email"] = result.user.email

            return redirect(url_for("dashboard"))

        except Exception:
            return "Invalid login credentials"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        try:
            # Create user in Supabase Auth ONLY
            result = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            return redirect(url_for("login"))

        except Exception as e:
            return f"Registration error: {e}"

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==================== MAIN PAGES ====================
@app.route("/")
def home():
    if not login_required():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("dashboard.html", name=session["user_email"])


@app.route("/assistant")
def assistant():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("assistant.html")


@app.route("/reports")
def reports():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("reports.html")


@app.route("/chatbot")
def chatbot_page():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("chatbot.html")


# ==================== CHATBOT API ====================
@app.route("/chatbot_api", methods=["POST"])
def chatbot_api():
    if "user_id" not in session:
        return jsonify({"reply": "Please login to continue."})

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    # Generate chatbot reply (TEXT)
    reply = medical_chatbot_response(user_message)

    # Speak reply (VOICE) – side effect only
    try:
        speak(reply)
    except Exception as e:
        print("TTS error:", e)

    # ALWAYS return text
    return jsonify({
        "reply": reply
    })
# ==================== RUN ====================
if __name__ == "__main__":
    app.run(debug=True)