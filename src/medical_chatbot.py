from src.medical_kb import MEDICAL_KNOWLEDGE

def medical_chatbot_response(user_message):
    text = user_message.lower()

    for key, data in MEDICAL_KNOWLEDGE.items():
        if key in text:
            response = f"🩺 Condition: {key.capitalize()}\n\n"
            response += f"ℹ️ Information: {data['info']}\n\n"

            if data["precautions"]:
                response += "✅ Precautions:\n"
                for p in data["precautions"]:
                    response += f"- {p}\n"
                response += "\n"

            if data["medicines"]:
                response += "💊 Common Medicines (informational only):\n"
                for m in data["medicines"]:
                    response += f"- {m}\n"
                response += "\n"

            response += f"👨‍⚕️ Medical Advice: {data['doctor']}"
            return response

    return (
        "I can assist with medical information, symptoms, and precautions.\n"
        "Please describe your condition clearly.\n"
        "Consult a doctor for accurate diagnosis."
    )