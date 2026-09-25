import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


CRISIS_CONFIG = {
    "enabled": os.getenv("CRISIS_ENABLED", "true").lower() == "true",

    "log_incidents": os.getenv(
        "LOG_INCIDENTS", "true"
    ).lower() == "true",

    "alert_channels": {
        "email": os.getenv(
            "SEND_EMAIL_ALERTS", "false"
        ).lower() == "true",

        "sms": os.getenv(
            "SEND_SMS_ALERTS", "false"
        ).lower() == "true",

        "webhook": os.getenv(
            "SEND_WEBHOOK_ALERTS", "false"
        ).lower() == "true",
    },

    "guardian_emails": [
        email.strip()
        for email in os.getenv("GUARDIAN_EMAILS", "").split(",")
        if email.strip()
    ],

    "admin_emails": [
        email.strip()
        for email in os.getenv("ADMIN_EMAIL", "").split(",")
        if email.strip()
    ],

    "sms_phone": os.getenv("ALERT_PHONE", ""),

    "webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),

    "restricted_mode": {
        "enabled": os.getenv(
            "RESTRICTED_MODE_ENABLED", "true"
        ).lower() == "true",

        "applies_to": [
            "self_harm_high",
            "violence_high"
        ]
    }
}


def handle_crisis(filter_result):
    result = filter_result.copy()

    category = filter_result.get("category")
    risk_level = filter_result.get("risk_level")
    crisis = filter_result.get("crisis", False)
    guardian_alert = filter_result.get("guardian_alert", False)

    alerts_sent = []
    incident_logged = False
    restricted_mode = False

    if crisis or risk_level == "high":
        if CRISIS_CONFIG["log_incidents"]:
            incident_logged = _log_incident(filter_result)

    if crisis:
        alerts_sent = _send_crisis_alerts(filter_result)

    elif guardian_alert:
        alerts_sent = _send_guardian_alerts(filter_result)

    if CRISIS_CONFIG["restricted_mode"]["enabled"]:
        restriction_key = f"{category}_{risk_level}"

        if restriction_key in CRISIS_CONFIG["restricted_mode"]["applies_to"]:
            restricted_mode = True

    result.update({
        "alerts_sent": alerts_sent,
        "incident_logged": incident_logged,
        "restricted_mode": restricted_mode
    })

    return result


def _log_incident(filter_result):
    try:
        os.makedirs("logs", exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": filter_result.get("category"),
            "risk_level": filter_result.get("risk_level"),
            "action": filter_result.get("action"),
            "crisis": filter_result.get("crisis", False),
            "guardian_alert": filter_result.get("guardian_alert", False)
        }

        with open(
            "logs/incidents.jsonl",
            "a",
            encoding="utf-8"
        ) as file:
            file.write(json.dumps(log_entry) + "\n")

        return True

    except Exception as e:
        print(f"Error logging incident: {e}")
        return False


def _send_crisis_alerts(filter_result):
    alerts_sent = []

    if not CRISIS_CONFIG["enabled"]:
        return alerts_sent

    if CRISIS_CONFIG["alert_channels"]["email"]:
        recipients = CRISIS_CONFIG["admin_emails"]

        if recipients:
            _send_email_alert(
                recipients=recipients,
                subject="CRISIS ALERT",
                body={
                    "category": filter_result.get("category"),
                    "risk_level": filter_result.get("risk_level"),
                    "action": filter_result.get("action")
                }
            )

            alerts_sent.append("email")

    if (
        CRISIS_CONFIG["alert_channels"]["sms"]
        and CRISIS_CONFIG["sms_phone"]
    ):
        _send_sms_alert(
            phone=CRISIS_CONFIG["sms_phone"],
            message=(
                f"Crisis alert: "
                f"{filter_result.get('category')} "
                f"{filter_result.get('risk_level')}"
            )
        )

        alerts_sent.append("sms")

    if (
        CRISIS_CONFIG["alert_channels"]["webhook"]
        and CRISIS_CONFIG["webhook_url"]
    ):
        _send_webhook_alert(filter_result)
        alerts_sent.append("webhook")

    return alerts_sent


def _send_guardian_alerts(filter_result):
    alerts_sent = []

    if not CRISIS_CONFIG["enabled"]:
        return alerts_sent

    if not CRISIS_CONFIG["alert_channels"]["email"]:
        return alerts_sent

    recipients = CRISIS_CONFIG["guardian_emails"]

    if not recipients:
        return alerts_sent

    _send_email_alert(
        recipients=recipients,
        subject="Safety Alert",
        body={
            "category": filter_result.get("category"),
            "risk_level": filter_result.get("risk_level"),
            "action": filter_result.get("action")
        }
    )

    alerts_sent.append("email")

    return alerts_sent


def _send_email_alert(recipients, subject, body):
    print(
        f"[EMAIL] To: {recipients}, "
        f"Subject: {subject}, "
        f"Body: {body}"
    )


def _send_sms_alert(phone, message):
    print(
        f"[SMS] To: {phone}, "
        f"Message: {message}"
    )


def _send_webhook_alert(filter_result):
    print(
        f"[WEBHOOK] URL: "
        f"{CRISIS_CONFIG['webhook_url']}"
    )

    print(
        f"[WEBHOOK] Data: {filter_result}"
    )


def update_config(new_config):
    global CRISIS_CONFIG

    CRISIS_CONFIG.update(new_config)