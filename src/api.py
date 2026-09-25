from flask import Flask, request, jsonify
from flask_cors import CORS
from src.detector import detect
from src.response_filter import filter_response
from src.crisis_handler import handle_crisis

app = Flask(__name__)
CORS(app) 


# Simple in-memory counter for medium-risk events per user
medium_risk_counter = {}


@app.route('/detect', methods=['POST'])
def detect_risk():
    """
    Complete safety detection pipeline with repeated medium-risk escalation.
    
    Message → Detector → Escalation Check → Filter → Crisis Handler → Result
    
    Optional fields:
    - user_id: Track repeated medium-risk events for this user (escalates after 3)
    """

    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message")
        user_id = data.get("user_id")  # Optional

        if not message or not isinstance(message, str):
            return jsonify({
                "error": "A valid message field is required"
            }), 400

        # STEP 1: Hakeem's Detection
        detection = detect(message)
        
        # STEP 1.5: Check for repeated medium-risk escalation
        escalated_from_medium = False
        if user_id and detection["risk_level"] == "medium":
            # Increment counter for this user
            if user_id not in medium_risk_counter:
                medium_risk_counter[user_id] = 0
            
            medium_risk_counter[user_id] += 1
            
            # After 3 medium events, escalate to high
            if medium_risk_counter[user_id] >= 3:
                detection["risk_level"] = "high"
                escalated_from_medium = True
                # Reset counter after escalation
                medium_risk_counter[user_id] = 0

        # STEP 2: Hamdallah's Response Filtering
        filter_result = filter_response({
            "category": detection["category"],
            "risk_level": detection["risk_level"],
            "confidence": detection.get("confidence", 0.0)
        })

        # STEP 3: Hamdallah's Crisis Handling
        crisis_result = handle_crisis(filter_result)

        # Build complete response
        response = {
            # Detection results (Hakeem)
            "detection": {
                "message": message,
                "category": detection["category"],
                "risk_level": detection["risk_level"],
                "confidence": detection.get("confidence", 0.0)
            },
            # Filtering results (Hamdallah - Filter)
            "filtering": {
                "action": crisis_result["action"],
                "replacement_response": crisis_result["replacement_response"]
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
   app.run(host="0.0.0.0", port=5000, debug=True)