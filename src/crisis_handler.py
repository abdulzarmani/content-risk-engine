import json
from datetime import datetime


# Configuration (can be moved to config/crisis_config.py later)
CRISIS_CONFIG = {
    "enabled": True,
    "log_incidents": True,
    "alert_channels": {
        "email": True,
        "sms": False,
        "webhook": False
    },
    "guardian_emails": [
        "parent@example.com",
        "guardian@example.com"
    ],
    "restricted_mode": {
        "enabled": True,
        "applies_to": ["self_harm_high", "violence_high"]
    }
}


def handle_crisis(filter_result):
    """
    Hamdallah's Crisis Handler.
    
    Takes response filter output and routes crisis alerts,
    logs incidents, and applies restrictions.
    
    Input:
    {
        "category": "self_harm",
        "risk_level": "high",
        "action": "block",
        "crisis": True,
        "guardian_alert": True,
        "replacement_response": "..."
    }
    
    Output:
    {
        "category": "self_harm",
        "risk_level": "high",
        "action": "block",
        "crisis": True,
        "guardian_alert": True,
        "replacement_response": "...",
        "alerts_sent": ["email"],
        "incident_logged": True,
        "restricted_mode": True
    }
    """
    
    result = filter_result.copy()
    
    category = filter_result.get("category")
    risk_level = filter_result.get("risk_level")
    crisis = filter_result.get("crisis", False)
    guardian_alert = filter_result.get("guardian_alert", False)
    
    # Track what actions we take
    alerts_sent = []
    incident_logged = False
    restricted_mode = False
    
    # 1. Log incident if crisis or high-risk
    if crisis or risk_level == "high":
        if CRISIS_CONFIG.get("log_incidents"):
            _log_incident(filter_result)
            incident_logged = True
    
    # 2. Send alerts
    if crisis:
        alerts_sent = _send_crisis_alerts(filter_result)
    elif guardian_alert:
        alerts_sent = _send_guardian_alerts(filter_result)
    
    # 3. Apply restricted mode
    if CRISIS_CONFIG.get("restricted_mode", {}).get("enabled"):
        restriction_key = f"{category}_{risk_level}"
        if restriction_key in CRISIS_CONFIG["restricted_mode"].get("applies_to", []):
            restricted_mode = True
    
    # Add crisis handler results to response
    result.update({
        "alerts_sent": alerts_sent,
        "incident_logged": incident_logged,
        "restricted_mode": restricted_mode
    })
    
    return result


def _log_incident(filter_result):
    """Log incident to file (expandable to database later)."""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": filter_result.get("category"),
            "risk_level": filter_result.get("risk_level"),
            "action": filter_result.get("action"),
            "crisis": filter_result.get("crisis"),
        }
        
        with open("logs/incidents.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error logging incident: {e}")


def _send_crisis_alerts(filter_result):
    """Send alerts for CRISIS cases."""
    alerts_sent = []
    
    category = filter_result.get("category")
    risk_level = filter_result.get("risk_level")
    
    if not CRISIS_CONFIG.get("enabled"):
        return alerts_sent
    
    # Email alerts
    if CRISIS_CONFIG["alert_channels"].get("email"):
        _send_email_alert(
            recipients=["admin@safetykitapp.com"],
            subject=f"CRISIS ALERT: {category.upper()} / {risk_level.upper()}",
            body=f"High-risk incident detected: {category} at {risk_level} level"
        )
        alerts_sent.append("email")
    
    # SMS alerts (if configured)
    if CRISIS_CONFIG["alert_channels"].get("sms"):
        _send_sms_alert(
            phone="+1234567890",
            message=f"Crisis Alert: {category} detected"
        )
        alerts_sent.append("sms")
    
    # Webhook (if configured)
    if CRISIS_CONFIG["alert_channels"].get("webhook"):
        _send_webhook_alert(filter_result)
        alerts_sent.append("webhook")
    
    return alerts_sent


def _send_guardian_alerts(filter_result):
    """Send alerts to guardians."""
    alerts_sent = []
    
    if not CRISIS_CONFIG.get("enabled"):
        return alerts_sent
    
    category = filter_result.get("category")
    
    # Email to guardians
    if CRISIS_CONFIG["alert_channels"].get("email"):
        recipients = CRISIS_CONFIG.get("guardian_emails", [])
        if recipients:
            _send_email_alert(
                recipients=recipients,
                subject=f"Safety Alert: Possible {category.replace('_', ' ')}",
                body=f"We detected a potentially concerning message. Please check in with your child."
            )
            alerts_sent.append("email")
    
    return alerts_sent


def _send_email_alert(recipients, subject, body):
    """
    Send email alert.
    TODO: Implement with SMTP or email service (SendGrid, AWS SES, etc.)
    """
    print(f"[EMAIL] To: {recipients}, Subject: {subject}")
    # Implementation placeholder


def _send_sms_alert(phone, message):
    """
    Send SMS alert.
    TODO: Implement with Twilio or similar service
    """
    print(f"[SMS] To: {phone}, Message: {message}")
    # Implementation placeholder


def _send_webhook_alert(filter_result):
    """
    Send webhook alert to external service.
    TODO: Implement with requests library
    """
    print(f"[WEBHOOK] Sending incident data...")
    # Implementation placeholder


def update_config(new_config):
    """Allow runtime configuration updates."""
    global CRISIS_CONFIG
    CRISIS_CONFIG.update(new_config)
    print("Crisis config updated")