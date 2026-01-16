def detect_intent(text):
    text = text.lower()
    if "fever" in text:
        return "Fever"
    if "cough" in text:
        return "Cough"
    if "headache" in text:
        return "Headache"
    return "General Inquiry"