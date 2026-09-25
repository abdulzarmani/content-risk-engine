import joblib
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

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

# TUNED TF-IDF VECTORIZER
vectorizer = TfidfVectorizer(
    max_features=5000,  # Increased from 3000
    ngram_range=(1, 3),  # Added 3-grams for better context
    min_df=2,  # Ignore terms that appear in less than 2 docs
    max_df=0.8,  # Ignore terms in more than 80% of docs
    sublinear_tf=True  # Sublinear term frequency scaling
)

# Learn TF-IDF only from training data
X_train = vectorizer.fit_transform(X_train_text)

# Transform test data
X_test = vectorizer.transform(X_test_text)

print("Training messages:", len(X_train_text))
print("Testing messages:", len(X_test_text))
print()
print("Training feature matrix shape:", X_train.shape)
print("Testing feature matrix shape:", X_test.shape)
print()

print("Training risk levels:")
print(y_train.value_counts())
print()

# TUNED LOGISTIC REGRESSION
model = LogisticRegression(
    max_iter=2000,  # Increased from 1000
    C=0.5,  # Stronger regularization
    solver='lbfgs',
    class_weight='balanced'  # Weight classes inversely to frequency
)

model.fit(X_train, y_train)

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/risk_model.joblib")
joblib.dump(vectorizer, "models/risk_vectorizer.joblib")

print("Risk model saved (TUNED).")
print()

# Make predictions
y_pred = model.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)
print()
print("Classification Report:")
print(classification_report(y_test, y_pred))