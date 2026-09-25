
import joblib
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("data/raw/messages.csv")

# Remove missing values
df = df.dropna(subset=["message", "risk_level"])

# Clean text
df["cleaned_message"] = df["message"].str.lower().str.strip()

# Separate input and target
text = df["cleaned_message"]
y = df["risk_level"]

# Split the dataset
X_train_text, X_test_text, y_train, y_test = train_test_split(
    text,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 2)
)

# Learn TF-IDF only from training data
X_train = vectorizer.fit_transform(X_train_text)

# Transform test data using the same vectorizer
X_test = vectorizer.transform(X_test_text)

print("Training messages:", len(X_train_text))
print("Testing messages:", len(X_test_text))

print()
print("Training risk levels:")
print(y_train.value_counts())

print()
print("Testing risk levels:")
print(y_test.value_counts())

print()
print("Training feature matrix:", X_train.shape)
print("Testing feature matrix:", X_test.shape)




from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Train the model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/risk_model.joblib")
joblib.dump(vectorizer, "models/risk_vectorizer.joblib")

print("Risk model saved.")

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

print()
print("Accuracy:", accuracy)

print()
print("Classification Report:")
print(classification_report(y_test, y_pred))