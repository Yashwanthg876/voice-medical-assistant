import random

def predict_disease(image_path):
    """
    Demo medical image prediction.
    Later this can be replaced with a real CNN model.
    """

    possible_results = [
        ("Normal", 0.90),
        ("Pneumonia Detected", 0.85),
        ("Possible Infection", 0.78),
        ("Abnormality Detected", 0.82)
    ]

    prediction, confidence = random.choice(possible_results)

    return {
        "prediction": prediction,
        "confidence": confidence
    }