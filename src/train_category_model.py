
import joblib
import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("data/raw/messages.csv")

# Clean text
df["cleaned_message"] = df["message"].str.lower().str.strip()

# Input and target
text = df["cleaned_message"]
y = df["category"]

# Split the data
X_train_text, X_test_text, y_train, y_test = train_test_split(
    text,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 2)
)

X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Create models directory
os.makedirs("models", exist_ok=True)

# Save model and vectorizer
joblib.dump(model, "models/category_model.joblib")
joblib.dump(vectorizer, "models/category_vectorizer.joblib")

print("Category model saved.")

# Predict
y_pred = model.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)

print("Training messages:", len(X_train_text))
print("Testing messages:", len(X_test_text))
print()
print("Accuracy:", accuracy)
print()
print("Classification Report:")
print(classification_report(y_test, y_pred))