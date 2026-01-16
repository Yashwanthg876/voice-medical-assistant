import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 170)     # speech speed
engine.setProperty("volume", 1.0)   # volume (0.0 to 1.0)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS ERROR:", e)