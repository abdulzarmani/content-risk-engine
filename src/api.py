import os
from threading import Lock

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.detector import detect
from src.response_filter import filter_response
from src.crisis_handler import handle_crisis

app = Flask(__name__)
CORS(app) 


# Simple in-memory counter for medium-risk events per user
medium_risk_counter = {}
medium_risk_lock = Lock()


def _guardian_alert_required(category, risk_level):
    if category in ("self_harm", "violence"):
        return risk_level in ("medium", "high")
    return category == "ai_dependency" and risk_level == "high"


@app.route('/detect', methods=['POST'])
def detect_risk():
    """
    Complete safety detection pipeline with repeated medium-risk escalation.
    
    Message → Detector → Escalation Check → Filter → Crisis Handler → Result
    
    Optional fields:
    - user_id: Track repeated medium-risk events for this user (escalates after 3)
    """

    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            data = {}

        message = data.get("message")
        user_id = data.get("user_id")

        if not isinstance(message, str) or not message.strip():
            return jsonify({
                "error": "A valid message field is required"
            }), 400
        if user_id is not None and not isinstance(user_id, str):
            return jsonify({"error": "user_id must be a string"}), 400
        if user_id is not None:
            user_id = user_id.strip() or None

        # STEP 1: Hakeem's Detection
        detection = detect(message)
        category = detection["category"]
        risk_level = detection.get("risk_level", detection.get("risk"))
        
        # STEP 1.5: Check for repeated medium-risk escalation
        escalated_from_medium = False
        if user_id and risk_level == "medium":
            with medium_risk_lock:
                medium_risk_counter[user_id] = medium_risk_counter.get(user_id, 0) + 1

                # After 3 medium events, escalate to high.
                if medium_risk_counter[user_id] >= 3:
                    risk_level = "high"
                    escalated_from_medium = True
                    medium_risk_counter[user_id] = 0

        # STEP 2: Hamdallah's Response Filtering
        filter_result = filter_response({
            "category": category,
            "risk_level": risk_level,
            "confidence": detection.get("confidence", 0.0)
        })

        # Adapt the filter contract to the fields required by crisis handling.
        crisis_context = {
            **filter_result,
            "category": category,
            "risk_level": risk_level,
            "guardian_alert": filter_result.get(
                "guardian_alert", _guardian_alert_required(category, risk_level)
            )
        }

        # STEP 3: Hamdallah's Crisis Handling
        crisis_result = handle_crisis(crisis_context)

        # Build complete response
        response = {
            # Detection results (Hakeem)
            "detection": {
                "message": message,
                "category": category,
                "risk_level": risk_level,
                "confidence": detection.get("confidence", 0.0)
            },
            # Filtering results (Hamdallah - Filter)
            "filtering": {
                "action": crisis_result["action"],
                "replacement_response": crisis_result.get(
                    "replacement", crisis_result.get("replacement_response")
                ),
                "message_to_user": crisis_result.get("message_to_user")
            },
            # Crisis handling results (Hamdallah - Crisis)
            "crisis_handling": {
                "crisis": crisis_result["crisis"],
                "guardian_alert": crisis_result["guardian_alert"],
                "alerts_sent": crisis_result["alerts_sent"],
                "incident_logged": crisis_result["incident_logged"],
                "restricted_mode": crisis_result["restricted_mode"]
            },
            # Escalation indicator
            "escalated_from_medium": escalated_from_medium
        }
        
        # Include user context if provided
        if user_id:
            response["user_id"] = user_id
            with medium_risk_lock:
                response["medium_risk_count"] = medium_risk_counter.get(user_id, 0)

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy"
    }), 200


if __name__ == '__main__':
    app.run(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    )