# Content Risk Engine – Content Detection Module

## What I Completed

I developed the initial **Content Detection Module** for the project.

The project now also includes a Flask API, a configurable decision/action layer, and configurable deployment resources so other modules can integrate with the detector.

The module takes a message and detects:

- The content category
- The risk level
- A confidence score for the predicted category

The module does **not** decide what action to take. Its output is passed to the next layer of the system.

## Detection Flow

```text
Message
   ↓
Content Detection Module
   ↓
Category + Risk Level + Confidence
   ↓
Decision/Action Layer
```

## Categories

The current model detects:

- `safe`
- `self_harm`
- `violence`
- `dangerous_instructions`
- `ai_dependency`

## Risk Levels

The risk model returns:

- `low`
- `medium`
- `high`

## Machine Learning

The current implementation uses:

- TF-IDF for converting text into numerical features
- Logistic Regression for classification
- Joblib for saving and loading the trained models

Two models were created:

1. Category Model
2. Risk Model

## Dataset

The dataset is located at:

```text
data/raw/messages.csv
```

It currently contains **750 messages**:

```text
150 safe
150 self_harm
150 violence
150 dangerous_instructions
150 ai_dependency
```

The dataset columns are:

```text
id
message
category
risk_level
```

## Files Created

```text
src/
├── prepare_data.py
├── train_category_model.py
├── test_category_model.py
├── test_model.py
├── detector.py
└── test_detector.py
```

The trained models are stored in:

```text
models/
├── category_model.joblib
├── category_vectorizer.joblib
├── risk_model.joblib
└── risk_vectorizer.joblib
```

## Main Detection File

The main file to use is:

```text
src/detector.py
```

It provides:

```python
detect(message)
```

Example:

```python
from detector import detect

result = detect("You are the only person who understands me.")

print(result)
```

It returns:

```python
{
    "message": "You are the only person who understands me.",
    "category": "ai_dependency",
    "risk_level": "high",
    "confidence": 0.6193
}
```

## Decision Layer

The decision/action rules are located in:

```text
src/decision_layer.py
```

The decision layer receives:

```text
category
risk_level
```

and returns:

```text
action
severity
message
resources
```

For example:

```text
self_harm + high
        ↓
CRISIS_ALERT
```

or:

```text
dangerous_instructions + high
        ↓
BLOCK_AND_REPORT
```

The detection module itself does not contain these action rules.

## Configurable Safety Resources

Location-specific resources are stored separately in:

```text
config/resources.py
```

The current file contains placeholder resources such as:

```python
SELF_HARM_RESOURCES = [
    "Local crisis service",
    "Mental health counselor",
    "Trusted friend or family member"
]
```

These should be updated for the location where the larger system will be deployed.

Keeping these resources outside `decision_layer.py` means deployment-specific resources can be changed without changing the main decision logic.

## API

The Flask API is located at:

```text
src/api.py
```

It provides:

```text
GET  /health
POST /detect
```

Health check:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
    "status": "healthy"
}
```

Detection example:

```bash
curl -X POST http://localhost:5000/detect   -H "Content-Type: application/json"   -d '{"message": "Can you explain how DNS works?"}'
```

The response contains the original message, category, risk level, confidence, action, severity, user-facing message, and resources.

Example:

```json
{
    "action": "ALLOW",
    "category": "safe",
    "confidence": 0.7274,
    "message": "Can you explain how DNS works?",
    "message_to_user": null,
    "resources": [],
    "risk_level": "low",
    "severity": "NONE"
}
```

## How the Other Modules Should Continue

The next modules should use the output from the detector.

```text
Message
   ↓
detector.py
   ↓
{
    category,
    risk_level,
    confidence
}
   ↓
Decision Layer
   ↓
Action
   ↓
API / Larger Safety System
```

The main integration points are:

```text
src/detector.py
src/decision_layer.py
src/api.py
config/resources.py
```

## How to Run

Activate the virtual environment:

```bash
source .venv/Scripts/activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Test the detector:

```bash
python src/test_detector.py
```

Run the challenging test cases:

```bash
python src/test_challenging.py
```

Start the Flask API from the project root:

```bash
python -m src.api
```

The API runs on:

```text
http://127.0.0.1:5000
```

Keep the API terminal running while testing `/health` and `/detect`.

## Current Model Performance

The tuned risk model was evaluated on a 150-message test set.

Current result:

```text
Accuracy: 85.33%
```

Classification report:

```text
              precision    recall  f1-score   support

high             0.93      0.81      0.87        64
low              0.78      0.97      0.87        30
medium           0.82      0.84      0.83        56

accuracy                           0.85       150
macro avg         0.85      0.87      0.85       150
weighted avg      0.86      0.85      0.85       150
```

The challenging test cases currently show:

```text
Category accuracy: 18/20
Risk accuracy:     14/20
Overall:           12/20
```

These challenging-test results are for additional testing and debugging. They should not be treated as the official held-out model accuracy.

## Current Status

The following parts are currently working:

- 750-message dataset
- 5 content categories
- 3 risk levels
- TF-IDF text features
- Category classification model
- Tuned risk classification model
- Saved Joblib models and vectorizers
- Content detector
- Category confidence score
- Decision/action layer
- Configurable safety resources
- Flask API
- `/health` endpoint
- `/detect` endpoint
- Basic detector tests
- Challenging test cases

The API has been tested locally with safe, self-harm, violence, AI-dependency, and dangerous-instruction examples.

## Known Limitations

The system is a machine-learning prototype and is not a perfect safety classifier.

The model can make mistakes, especially with:

- indirect language
- ambiguous language
- unusual wording
- messages where the risk level is difficult to determine
- messages that are similar across categories

The challenging tests have already identified some of these cases.

The dataset and models should therefore continue to be evaluated and improved before production deployment.

## Recommended Next Development Work

The next team can continue with:

1. Connecting the API to the larger safety system.
2. Improving the dataset with more varied and realistic examples.
3. Adding more difficult and ambiguous test cases.
4. Improving category classification where errors occur.
5. Improving risk-level classification.
6. Evaluating precision, recall, and F1-score as the dataset changes.
7. Adding automated API tests.
8. Replacing placeholder safety resources with appropriate local resources.
9. Reviewing the decision rules before deployment.
10. Preparing the API for the deployment environment.

## Important Development Note

Do not add large collections of individual test messages directly into `detector.py` just to make specific tests pass.

The intended separation is:

```text
Training Dataset
      ↓
Machine Learning Models
      ↓
detector.py
      ↓
Category + Risk Level
      ↓
decision_layer.py
      ↓
Action
```

The ML models should learn from the dataset.

The decision layer should handle the predefined action rules.

This separation allows the models and safety policy to be improved independently.

## Project Structure

```text
content-risk-engine/
│
├── config/
│   ├── __init__.py
│   └── resources.py
│
├── data/
│   └── raw/
│       └── messages.csv
│
├── models/
│   ├── category_model.joblib
│   ├── category_vectorizer.joblib
│   ├── risk_model.joblib
│   └── risk_vectorizer.joblib
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── check_dataset.py
│   ├── decision_layer.py
│   ├── detector.py
│   ├── prepare_data.py
│   ├── test_category_model.py
│   ├── test_challenging.py
│   ├── test_detector.py
│   ├── test_model.py
│   ├── train_category_model.py
│   └── train_risk_model_tuned.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Handover

The project is ready for the next team to continue development.

### API Integration Contract

The larger system can send a message to:

```text
POST /detect
Content-Type: application/json
```

Request body:

```json
{
    "message": "User message here"
}
```

The API returns the detected category, risk level, category confidence, and the action selected by the decision layer.

The UI or larger safety system should use the API response rather than loading the ML models directly.

Before making changes, they should:

1. Create and activate their own Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run the detector tests.
4. Start the API with `python -m src.api`.
5. Test `/health` and `/detect`.
6. Review `src/detector.py`.
7. Review `src/decision_layer.py`.
8. Review `config/resources.py`.
9. Review the dataset before retraining the models.

The `.venv/` and `.venv_backup/` directories are intentionally excluded from Git. Each developer should create their own virtual environment.
