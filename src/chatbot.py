def medical_chatbot_response(user_input):
    user_input = user_input.lower()

    if "fever" in user_input:
        return "If you have a fever, rest well, stay hydrated, and consult a doctor if it persists."

    if "cough" in user_input:
        return "A cough can be due to infection or allergy. Drink warm fluids and seek medical advice if severe."

    if "headache" in user_input:
        return "Headaches can be caused by stress or dehydration. Rest and drink water."

    return "Please consult a healthcare professional for accurate diagnosis."