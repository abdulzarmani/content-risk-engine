from flask import Flask, request, jsonify
from src.detector import detect
from src.decision_layer import decide_action

app = Flask(__name__)


@app.route('/detect', methods=['POST'])
def detect_risk():
    """
    Receive a message and return its category, risk level,
    and recommended action.
    """

    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message")

        if not message or not isinstance(message, str):
            return jsonify({
                "error": "A valid message field is required"
            }), 400

        # Run ML detection
        detection = detect(message)

        # Apply decision rules
        action = decide_action(
            detection["category"],
            detection["risk_level"]
        )

        # Build standard response
        response = {
            "message": message,
            "category": detection["category"],
            "risk_level": detection["risk_level"],
            "action": action["action"],
            "severity": action["severity"],
            "message_to_user": action["message"],
            "resources": action["resources"]
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