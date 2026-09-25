import joblib


# Load the trained models
category_model = joblib.load("models/category_model.joblib")
category_vectorizer = joblib.load("models/category_vectorizer.joblib")

risk_model = joblib.load("models/risk_model.joblib")
risk_vectorizer = joblib.load("models/risk_vectorizer.joblib")


def detect(message):
    """
    Detect the category and risk level of a message.
    """

    # Clean the message
    cleaned_message = message.lower().strip()

    # Convert message to TF-IDF features
    category_features = category_vectorizer.transform([cleaned_message])
    risk_features = risk_vectorizer.transform([cleaned_message])

    # Make predictions
    category = category_model.predict(category_features)[0]
    risk_level = risk_model.predict(risk_features)[0]

    return {
    "message": message,
    "category": category,
    "risk_level": risk_level
}