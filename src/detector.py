import joblib
from textblob import TextBlob


# Load the trained models
category_model = joblib.load("models/category_model.joblib")
category_vectorizer = joblib.load("models/category_vectorizer.joblib")

risk_model = joblib.load("models/risk_model.joblib")
risk_vectorizer = joblib.load("models/risk_vectorizer.joblib")


def preprocess_message(message):
    """
    Clean, correct grammar/spelling, and normalize the message.
    """
    # Fix grammar and spelling using TextBlob
    blob = TextBlob(message)
    corrected = str(blob.correct())
    
    # Remove extra spaces and convert to lowercase
    cleaned = " ".join(corrected.split()).lower().strip()
    
    return cleaned


def is_message_complete(message):
    """
    Check if message has enough context for detection.
    Returns True if complete, False if too short.
    """
    words = message.strip().split()
    return len(words) >= 3


def context_aware_override(message, category, confidence):
    """
    Override ML prediction based on word pair context.
    Useful when ML confidence is low or prediction seems wrong.
    
    Args:
        message: str - the cleaned message
        category: str - ML predicted category
        confidence: float - ML prediction confidence
    
    Returns:
        str - original or overridden category
    """
    words = message.lower().split()
    
    # SELF_HARM patterns: trigger word + self-reference
    self_harm_patterns = [
        ("kill", ["myself", "me", "i"]),
        ("hurt", ["myself", "me"]),
        ("want", ["die", "end", "stop"]),
        ("end", ["it", "myself", "me"]),
        ("suicide", ["want", "commit", "i"])
    ]
    
    # VIOLENCE patterns: trigger word + other person
    violence_patterns = [
        ("kill", ["them", "him", "her", "someone", "people"]),
        ("hurt", ["them", "him", "her", "someone"]),
        ("punch", ["face", "him", "her"]),
        ("beat", ["them", "up", "him", "her"]),
        ("attack", ["them", "someone", "him", "her"]),
    ]
    
    # Check for self_harm patterns
    for trigger_word, target_words in self_harm_patterns:
        if trigger_word in words:
            for target in target_words:
                if target in words:
                    # Override to self_harm if confidence is low
                    if confidence < 0.7 and category != "self_harm":
                        return "self_harm"
    
    # Check for violence patterns
    for trigger_word, target_words in violence_patterns:
        if trigger_word in words:
            for target in target_words:
                if target in words:
                    # Override to violence if confidence is low
                    if confidence < 0.7 and category != "violence":
                        return "violence"
    
    # No override needed
    return category


def detect(message):
    """
    Detect the category, risk level, and confidence of a message.
    """
    
    # Check if message is complete enough
    if not is_message_complete(message):
        return {
            "message": message,
            "category": "safe",
            "risk_level": "low",
            "confidence": 0.0,
            "note": "Message too short. Please provide more context."
        }

    # Preprocess and correct the message
    cleaned_message = preprocess_message(message)

    # Convert message to TF-IDF features
    category_features = category_vectorizer.transform([cleaned_message])
    risk_features = risk_vectorizer.transform([cleaned_message])

    # Predict category
    category = category_model.predict(category_features)[0]

    # Get confidence for the predicted category
    category_probabilities = category_model.predict_proba(category_features)[0]
    confidence = float(category_probabilities.max())

    # Apply context-aware override for low confidence predictions
    category = context_aware_override(cleaned_message, category, confidence)

    # Predict risk level
    risk_level = risk_model.predict(risk_features)[0]

    return {
        "message": message,
        "category": category,
        "risk_level": risk_level,
        "confidence": round(confidence, 4)
    }