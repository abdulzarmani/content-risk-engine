import os
import torch
import torch.nn.functional as F
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

MODEL_PATH = "models/distilbert_safety_model"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

LABEL_TO_RISK = {
    "safe": "low",
    "ai_dependency": "medium",
    "dangerous_instructions": "high",
    "violence": "high",
    "self_harm": "high"
}

def preprocess_message(message: str) -> str:
    """Basic normalization for incoming chat text."""
    return " ".join(message.strip().split())

def detect(message: str) -> dict:
    """
    Run sequence classification inference using the fine-tuned DistilBERT model.
    """
    if not isinstance(message, str) or not message.strip():
        return {
            "message": message,
            "category": "safe",
            "risk_level": "low",
            "confidence": 0.0
        }

    cleaned = preprocess_message(message)

    # Tokenize input
    inputs = tokenizer(
        cleaned,
        truncation=True,
        padding=True,
        max_length=64,
        return_tensors="pt"
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0]
        confidence, predicted_idx = torch.max(probs, dim=-1)

    predicted_label = model.config.id2label[predicted_idx.item()]
    confidence_val = round(confidence.item(), 4)

    # Map category to default risk level
    risk_level = LABEL_TO_RISK.get(predicted_label, "low")

    # If confidence is borderline, temper the risk rating
    if predicted_label in ("violence", "self_harm") and confidence_val < 0.65:
        risk_level = "medium"

    return {
        "message": message,
        "category": predicted_label,
        "risk_level": risk_level,
        "confidence": confidence_val
    }

if __name__ == "__main__":
    test_phrases = [
        "I love hanging out with my friends and eating pizza.",
        "I want to unalive someone.",
        "I can't live without you, please don't log off.",
        "How do I build a pipe bomb?",
        "I want to put myself off the world."
    ]

    print("\n--- Running Local Verification ---\n")
    for phrase in test_phrases:
        res = detect(phrase)
        print(f"Text: '{res['message']}'")
        print(f" -> Category: {res['category']} | Risk: {res['risk_level']} | Conf: {res['confidence'] * 100:.1f}%\n")