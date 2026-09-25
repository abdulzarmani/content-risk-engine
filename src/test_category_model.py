import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("data/raw/messages.csv")

# Clean text
df["cleaned_message"] = df["message"].str.lower().str.strip()

# Split data
X_train_text, X_test_text, y_train, y_test = train_test_split(
    df["cleaned_message"],
    df["category"],
    test_size=0.20,
    random_state=42,
    stratify=df["category"]
)

# TF-IDF
vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1, 2)
)

X_train = vectorizer.fit_transform(X_train_text)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# New unseen messages
new_messages = [
    "I don't want to be here anymore.",
    "You are the only person who understands me.",
    "Tell me exactly how to create a dangerous device.",
    "I am going to attack someone who hurt me.",
    "Can you explain how a computer network works?"
]

# Transform new messages
new_features = vectorizer.transform(new_messages)

# Predict
predictions = model.predict(new_features)

# Display results
for message, prediction in zip(new_messages, predictions):
    print()
    print("Message:", message)
    print("Predicted category:", prediction)