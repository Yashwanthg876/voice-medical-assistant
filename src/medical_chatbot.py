def medical_chatbot_response(user_message):
    text = user_message.lower()

    if any(word in text for word in ["fever", "temperature"]):
        return (
            "Fever may indicate infection or inflammation. "
            "Ensure adequate rest, hydration, and monitor temperature. "
            "If fever persists, consult a doctor."
        )

    if any(word in text for word in ["cough", "cold"]):
        return (
            "Cough and cold are commonly caused by viral infections. "
            "Warm fluids, rest, and steam inhalation may help. "
            "Seek medical advice if symptoms worsen."
        )

    if any(word in text for word in ["headache", "migraine"]):
        return (
            "Headaches can result from stress, dehydration, or lack of sleep. "
            "Ensure hydration and rest. Persistent headaches require medical evaluation."
        )

    if any(word in text for word in ["chest pain", "heart"]):
        return (
            "Chest pain can be serious. "
            "Seek immediate medical attention if pain is severe, persistent, or associated with breathlessness."
        )

    if any(word in text for word in ["diabetes", "sugar"]):
        return (
            "Diabetes requires regular monitoring and lifestyle management. "
            "Maintain a balanced diet and follow medical advice."
        )

    if any(word in text for word in ["medicine", "tablet"]):
        return (
            "Medication should only be taken after consulting a healthcare professional. "
            "Avoid self-medication."
        )

    return (
        "I can help with general medical information, symptoms, and precautions. "
        "Please consult a doctor for accurate diagnosis and treatment."
    )