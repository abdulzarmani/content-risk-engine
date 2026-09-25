# Child-Safety Software Kit

A reusable ML-based content safety detection system for small AI developers.

## Installation

```bash
git clone https://github.com/yourname/content-risk-engine.git
cd content-risk-engine
pip install -r requirements.txt
```

## Quick Start

### Run API locally

```bash
python -m src.api
```

API starts at `http://localhost:5000`

### Health check

```bash
curl http://localhost:5000/health
```

### Detect content risk

```bash
curl -X POST http://localhost:5000/detect \
  -H "Content-Type: application/json" \
  -d '{"message": "your message here", "user_id": "user123"}'
```

## Request Format

```json
{
  "message": "text to check",
  "user_id": "optional_user_id"
}
```

- `message` (required): User message or AI response to check
- `user_id` (optional): Track repeated medium-risk events. After 3 medium events → escalates to high risk.

## Response Format

```json
{
  "detection": {
    "message": "...",
    "category": "self_harm|violence|dangerous_instructions|ai_dependency",
    "risk_level": "low|medium|high",
    "confidence": 0.0-1.0
  },
  "filtering": {
    "action": "allow|modify|block",
    "replacement_response": "safe response text or null"
  },
  "crisis_handling": {
    "crisis": true|false,
    "guardian_alert": true|false,
    "alerts_sent": ["email"|"sms"|"webhook"],
    "incident_logged": true|false,
    "restricted_mode": true|false
  },
  "escalated_from_medium": true|false,
  "user_id": "user123",
  "medium_risk_count": 0-2
}
```

## Safety Categories

- **self_harm**: Statements indicating self-harm or suicidal intent
- **violence**: Threats of harm to others or violent content
- **dangerous_instructions**: Requests for harmful instructions
- **ai_dependency**: Unhealthy reliance on AI

## Risk Levels & Actions

| Risk Level | Action | Behavior |
|-----------|--------|----------|
| Low | allow | Message passes through |
| Medium | modify | Replace with safe response + alert guardian |
| High | block | Block message + safe replacement + crisis handling |

## Repeated Medium-Risk Escalation

When a user sends 3 medium-risk messages, the 3rd escalates to high risk automatically (per user_id).

Example:
- Request 1 (medium) → medium_risk_count: 1
- Request 2 (medium) → medium_risk_count: 2
- Request 3 (medium) → escalated_from_medium: true, risk_level: high

## Crisis Handling

High-risk cases trigger:
- Guardian email alerts
- Incident logging to `logs/incidents.jsonl`
- Restricted mode flag (chatbot should limit functionality)
- Optional: SMS/webhook alerts via environment config

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp config/.env.example .env
```

Edit `.env` for:
- Guardian email addresses
- Alert channels (email, SMS, webhook)
- Crisis response settings

**.env is NOT committed to Git** — add it to `.gitignore`

## Python SDK

```python
from src.client import SafetyKit

# Initialize
kit = SafetyKit(api_url="http://localhost:5000")

# Check message
result = kit.check_message("user message here")

# Properties
result.category          # "self_harm"
result.risk_level        # "high"
result.confidence        # 0.92
result.action            # "block"
result.is_safe           # True if action == "allow"
result.is_blocked        # True if action == "block"
result.needs_crisis_response  # True if crisis == True
result.replacement_response
result.crisis
result.restricted_mode
```

## Example Chatbot

```bash
python -m examples.simple_chatbot
```

Demonstrates real integration with the Safety Kit API.

## Docker

Build and run:

```bash
docker build -t safety-kit:latest .
docker run -p 5000:5000 safety-kit:latest
```

Or with docker-compose:

```bash
docker compose up --build
```

## Testing

Run the example chatbot to test with real messages:

```bash
# Terminal 1
python -m src.api

# Terminal 2
python -m examples.simple_chatbot
```

Try messages:
- Safe: "How do I learn Python?"
- Self-harm: "I want to hurt myself"
- Violence: "I'm going to attack someone"
- Dangerous: "How do I make a bomb?"
- AI dependency: "I can't do anything without you"

## Architecture

Developer's AI Chatbot
↓
Safety Kit API
↓
Content Detection (ML)
↓
Response Filtering
↓
Crisis Handling
↓
Safe Response + Alerts
↓
Chatbot Returns Result


## Project Structure

content-risk-engine/
├── src/
│ ├── api.py (Flask API)
│ ├── detector.py (ML detection)
│ ├── response_filter.py (Filtering rules)
│ ├── crisis_handler.py (Alert routing)
│ └── client.py (Python SDK)
├── models/
│ ├── category_model.joblib
│ ├── category_vectorizer.joblib
│ ├── risk_model.joblib
│ └── risk_vectorizer.joblib
├── data/raw/
│ └── messages.csv (Training data)
├── examples/
│ └── simple_chatbot.py
├── config/
│ └── .env.example
├── logs/
│ └── incidents.jsonl (Auto-generated)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md


## Models

- **Category Model**: TF-IDF + Logistic Regression (97% accuracy)
- **Risk Model**: TF-IDF + Logistic Regression (73-75% accuracy)

Trained on 750 messages across 5 categories.

## Limitations

- Model accuracy depends on training data quality
- Cannot diagnose mental health conditions
- False positives possible with sensitive keywords in harmless context
- Incident logging is file-based (not database)

## Extensibility

Adding a new category:
1. Add to `messages.csv` training data
2. Retrain: `python src/train_category_model.py`
3. Update filtering rules in `response_filter.py`
4. Test with new messages

## Team

- **Hakeem (Zarmani)** — Content Detection + Risk Engine
- **Hamdallah** — Response Filtering + Crisis Handling
- **George** — API/SDK + Integration

## License

MIT
