import wave
import json
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-en-us-0.15"

model = Model(MODEL_PATH)

def speech_to_text(wav_path):
    wf = wave.open(wav_path, "rb")

    rec = KaldiRecognizer(model, wf.getframerate())
    text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "

    final_result = json.loads(rec.FinalResult())
    text += final_result.get("text", "")

    wf.close()
    return text.strip()