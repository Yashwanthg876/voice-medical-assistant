def detect_intent(text):
    text = text.lower()

    emergency_keywords = [
        "help", "emergency", "call ambulance", "heart attack",
        "fainted", "unconscious", "can't breathe", "severe pain"
    ]

    reminder_keywords = [
        "remind", "reminder", "medicine", "tablet", "pill",
        "appointment", "doctor visit"
    ]

    symptom_keywords = [
        "pain", "fever", "dizzy", "headache", "vomiting",
        "cough", "breathing", "chest pain", "weakness"
    ]

    for word in emergency_keywords:
        if word in text:
            return "EMERGENCY"

    for word in reminder_keywords:
        if word in text:
            return "REMINDER"

    for word in symptom_keywords:
        if word in text:
            return "SYMPTOM"

    return "GENERAL"