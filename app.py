from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__, static_folder="static")

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    return jsonify({"message": "Voice received (ASR will be added)"})

@app.route("/upload_image", methods=["POST"])
def upload_image():
    return jsonify({"message": "Image received (AI model will be added)"})

if __name__ == "__main__":
    app.run(debug=True)