import os
import time
from threading import Lock

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from src.detector import detect
from src.response_filter import filter_response
from src.crisis_handler import handle_crisis
from google import genai

app = Flask(__name__)
CORS(app) 

# ==========================================
# GEMINI CONFIGURATION (MODERN SDK)
# ==========================================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
medium_risk_counter = {}
medium_risk_lock = Lock()

def _guardian_alert_required(category, risk_level):
    if category in ("self_harm", "violence"):
        return risk_level in ("medium", "high")
    return category == "ai_dependency" and risk_level == "high"

def _build_response(message, category, risk_level, confidence, crisis_result, filter_result, escalated_from_medium, user_id=None):
    response = {
        "detection": {
            "message": message,
            "category": category,
            "risk_level": risk_level,
            "confidence": confidence
        },
        "filtering": {
            "action": str(crisis_result.get("action", "ALLOW")).upper(),
            "replacement_response": filter_result.get("replacement_response"),
            "message_to_user": crisis_result.get("message_to_user")
        },
        "crisis_handling": {
            "crisis": crisis_result.get("crisis", False),
            "guardian_alert": crisis_result.get("guardian_alert", False),
            "alerts_sent": crisis_result.get("alerts_sent", []),
            "incident_logged": crisis_result.get("incident_logged", False),
            "restricted_mode": crisis_result.get("restricted_mode", False)
        },
        "escalated_from_medium": escalated_from_medium
    }
    
    if user_id:
        response["user_id"] = user_id
        with medium_risk_lock:
            response["medium_risk_count"] = medium_risk_counter.get(user_id, 0)
            
    return response

@app.route('/detect', methods=['POST'])
def detect_risk():
    try:
        data = request.get_json(silent=True) or {}
        message = data.get("message")
        user_id = data.get("user_id")

        if not isinstance(message, str) or not message.strip():
            return jsonify({"error": "A valid message field is required"}), 400

        # ==========================================
        # CHECKPOINT 1: Scan User Message
        # ==========================================
        detection = detect(message)
        category = detection["category"]
        risk_level = detection.get("risk_level", detection.get("risk", "low"))
        
        escalated_from_medium = False
        if user_id and risk_level == "medium":
            with medium_risk_lock:
                medium_risk_counter[user_id] = medium_risk_counter.get(user_id, 0) + 1
                if medium_risk_counter[user_id] >= 3:
                    risk_level = "high"
                    escalated_from_medium = True
                    medium_risk_counter[user_id] = 0

        filter_result = filter_response({
            "category": category,
            "risk_level": risk_level,
            "confidence": detection.get("confidence", 0.0)
        })

        crisis_context = {
            **filter_result,
            "category": category,
            "risk_level": risk_level,
            "guardian_alert": filter_result.get("guardian_alert", _guardian_alert_required(category, risk_level))
        }

        crisis_result = handle_crisis(crisis_context)
        
        current_action = str(crisis_result.get("action", "ALLOW")).upper()
        
        # THE FINAL FIX: Only bypass Gemini if the engine explicitly screams "BLOCK"
        if current_action == "BLOCK":
            print(f"BLOCKED BY CHECKPOINT 1: {message}")
            return jsonify(_build_response(
                message, category, risk_level, detection.get("confidence", 0.0),
                crisis_result, filter_result, escalated_from_medium, user_id
            )), 200

        # ==========================================
        # THE BRAIN: Generate with Retry Logic
        # ==========================================
        print(f"\n--- SENDING TO GEMINI: {message} ---")
        
        max_retries = 3
        ai_text = "I am having trouble thinking right now."
        
        for attempt in range(max_retries):
            try:
                ai_response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=message
                )
                ai_text = ai_response.text
                print(f"--- GEMINI SAYS (Attempt {attempt + 1}): {ai_text} ---\n")
                break
            except Exception as e:
                print(f"--- ATTEMPT {attempt + 1} FAILED: {e} ---")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("\n--- ALL RETRIES FAILED ---")

        # ==========================================
        # CHECKPOINT 2: Scan AI Reply
        # ==========================================
        ai_detection = detect(ai_text)
        ai_risk = ai_detection.get("risk_level", ai_detection.get("risk", "low"))
        
        if ai_risk == "high" or ai_detection["category"] in ("self_harm", "violence", "dangerous_instructions"):
            print(f"[CRISIS AVERTED] AI tried to say: {ai_text}")
            crisis_result["action"] = "BLOCK"
            crisis_result["message_to_user"] = "I am sorry, but I cannot continue this specific conversation."
            filter_result["replacement_response"] = "I am sorry, but I cannot continue this specific conversation."
        else:
            crisis_result["message_to_user"] = ai_text
            filter_result["replacement_response"] = ai_text

        return jsonify(_build_response(
            message, category, risk_level, detection.get("confidence", 0.0),
            crisis_result, filter_result, escalated_from_medium, user_id
        )), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/')
def serve_ui():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(project_root, 'examples', 'web_demo.html')
    return send_file(html_path)

if __name__ == '__main__':
    app.run(host=os.getenv("API_HOST", "0.0.0.0"), port=int(os.getenv("API_PORT", "5000")), debug=False)