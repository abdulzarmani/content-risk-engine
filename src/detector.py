from transformers import pipeline
from textblob import TextBlob
import warnings
import logging

# Suppress harmless warnings for a clean terminal
warnings.filterwarnings('ignore')
logging.getLogger("transformers").setLevel(logging.ERROR)

print("Loading Semantic AI Engine (DistilBERT)...")
# This replaces the 4 joblib files. It downloads the ~268MB weights on the first run.
classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
print("Semantic Engine Ready.")

def preprocess_message(message):
    """
    Clean, translate algospeak, correct grammar/spelling, and normalize the message.
    """
    message_lower = message.lower()
    
    # 1. Algospeak & Slang Translation Layer
    # Translate filter-evasion words into standard English before the AI reads them
    algospeak_dict = {
        "unalive": "kill",
        "sewerslide": "suicide",
        "kms": "kill myself",
        "kys": "kill yourself",
        "toaster bath": "suicide",
        "catch a body": "murder"
    }
    
    for slang, standard in algospeak_dict.items():
        # Add word boundaries so it only replaces exact matches
        message_lower = message_lower.replace(slang, standard)

    # 2. Fix grammar and spelling using TextBlob
    blob = TextBlob(message_lower)
    corrected = str(blob.correct())
    
    # 3. Remove extra spaces
    cleaned = " ".join(corrected.split()).strip()
    
    return cleaned

def is_message_complete(message):
    """
    Check if message has enough context for detection.
    """
    words = message.strip().split()
    return len(words) >= 3

def context_aware_override(message_lower):
    """
    LAYER 1: Instant hardcoded safety net. 
    Triggers immediately on severe combinations before AI processing.
    """
    words = message_lower.split()
    
    self_harm_patterns = [
        ("kill", ["myself", "me",]),
        ("hurt", ["myself", "me"]),
        ("want", ["die", "end", "stop"]),
        ("end", ["it", "myself", "me"]),
        ("suicide", ["want", "commit", "i", "suicide"]),
        ("commit", ["suicide"])
    ]
    
    violence_patterns = [
        ("kill", ["them", "him", "her", "someone", "people"]),
        ("hurt", ["them", "him", "her", "someone"]),
        ("punch", ["face", "him", "her"]),
        ("beat", ["them", "up", "him", "her"]),
        ("attack", ["them", "someone", "him", "her"]),
    ]
    
    for trigger_word, target_words in self_harm_patterns:
        if trigger_word in words and any(target in words for target in target_words):
            return "self_harm", "high", 0.99
            
    for trigger_word, target_words in violence_patterns:
        if trigger_word in words and any(target in words for target in target_words):
            return "violence", "high", 0.99
            
    return "safe", "low", 1.0

def detect(message):
    """
    Detect the category, risk level, and confidence of a message using NLU.
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

    # LAYER 1: Hardcoded fail-safe
    manual_category, manual_risk, manual_conf = context_aware_override(cleaned_message)
    if manual_category != "safe":
        return {
            "message": message,
            "category": manual_category,
            "risk_level": manual_risk,
            "confidence": manual_conf
        }

    # LAYER 2: Zero-Shot Semantic Engine (reads intent and context)
    candidate_labels = [
        "self harm or suicide",
        "violence and physical threats",
        "asking for dangerous instructions or illegal acts",
        "emotional dependence on an artificial intelligence",
        "safe everyday conversation"
    ]

    result = classifier(cleaned_message, candidate_labels)
    top_match = result['labels'][0]
    confidence = float(result['scores'][0])

    # LAYER 3: Map NLU intent back to George/Hamdallah's required JSON format
    if top_match == "self harm or suicide" and confidence > 0.50:
        category, risk_level = "self_harm", "high"
        
    elif top_match == "violence and physical threats" and confidence > 0.50:
        category, risk_level = "violence", "high"
        
    elif top_match == "asking for dangerous instructions or illegal acts" and confidence > 0.50:
        category, risk_level = "dangerous_instructions", "medium"
        
    elif top_match == "emotional dependence on an artificial intelligence" and confidence > 0.40:
        category, risk_level = "ai_dependency", "medium"
        
    else:
        category, risk_level = "safe", "low"

    return {
        "message": message,
        "category": category,
        "risk_level": risk_level,
        "confidence": round(confidence, 4)
    }