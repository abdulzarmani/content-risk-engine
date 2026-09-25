from flask import Flask, request, jsonify
from src.detector import detect
from src.response_filter import filter_response
from src.crisis_handler import handle_crisis

app = Flask(__name__)


@app.route('/detect', methods=['POST'])
def detect_risk():
    """
    Complete safety detection pipeline.
    
    Message → Detector → Filter → Crisis Handler → Result
    
    Returns full detection, filtering, and crisis handling result.
    """

    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message")

        if not message or not isinstance(message, str):
            return jsonify({
                "error": "A valid message field is required"
            }), 400

        # STEP 1: Hakeem's Detection
        detection = detect(message)

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
            }
        }

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
    app.run(debug=True, port=5000)