from config.resources import (
    SELF_HARM_RESOURCES,
    VIOLENCE_RESOURCES,
    AI_DEPENDENCY_RESOURCES
)


def decide_action(category, risk_level):
    """
    Decision rules: Takes ML detector output and returns
    what action the system should take.

    Args:
        category: str - one of [safe, self_harm, violence,
                        dangerous_instructions, ai_dependency]
        risk_level: str - one of [low, medium, high]

    Returns:
        dict with action, severity, message, and resources
    """

    rules = {
        # SELF_HARM
        ("self_harm", "high"): {
            "action": "CRISIS_ALERT",
            "severity": "CRITICAL",
            "message": "We're concerned about your safety. Please reach out to a crisis service.",
            "resources": SELF_HARM_RESOURCES
        },

        ("self_harm", "medium"): {
            "action": "SUPPORT_OFFER",
            "severity": "HIGH",
            "message": "We notice you're struggling. Would you like to talk to someone or get support resources?",
            "resources": SELF_HARM_RESOURCES
        },

        ("self_harm", "low"): {
            "action": "MONITOR",
            "severity": "LOW",
            "message": None,
            "resources": []
        },

        # VIOLENCE
        ("violence", "high"): {
            "action": "SAFETY_ALERT",
            "severity": "CRITICAL",
            "message": "This describes intent to harm others. We take this seriously.",
            "resources": VIOLENCE_RESOURCES
        },

        ("violence", "medium"): {
            "action": "AWARENESS",
            "severity": "MEDIUM",
            "message": "You seem to be having hostile thoughts. Consider talking to someone.",
            "resources": VIOLENCE_RESOURCES
        },

        ("violence", "low"): {
            "action": "MONITOR",
            "severity": "LOW",
            "message": None,
            "resources": []
        },

        # AI_DEPENDENCY
        ("ai_dependency", "high"): {
            "action": "REALITY_CHECK",
            "severity": "MEDIUM",
            "message": "We notice you're becoming very dependent on AI. Real human connections are important for your wellbeing.",
            "resources": AI_DEPENDENCY_RESOURCES
        },

        ("ai_dependency", "medium"): {
            "action": "GENTLE_NUDGE",
            "severity": "LOW",
            "message": "Consider balancing AI conversations with real-world relationships.",
            "resources": AI_DEPENDENCY_RESOURCES
        },

        ("ai_dependency", "low"): {
            "action": "ALLOW",
            "severity": "NONE",
            "message": None,
            "resources": []
        },

        # DANGEROUS_INSTRUCTIONS
        ("dangerous_instructions", "high"): {
            "action": "BLOCK_AND_REPORT",
            "severity": "CRITICAL",
            "message": "Request for harmful instructions blocked. This may be reported.",
            "resources": []
        },

        ("dangerous_instructions", "medium"): {
            "action": "FLAG_FOR_REVIEW",
            "severity": "MEDIUM",
            "message": "This request needs human review due to safety concerns.",
            "resources": []
        },

        ("dangerous_instructions", "low"): {
            "action": "ALLOW",
            "severity": "NONE",
            "message": None,
            "resources": []
        },

        # SAFE
        ("safe", "low"): {
            "action": "ALLOW",
            "severity": "NONE",
            "message": None,
            "resources": []
        },

        ("safe", "medium"): {
            "action": "ALLOW",
            "severity": "NONE",
            "message": None,
            "resources": []
        },

        ("safe", "high"): {
            "action": "ALLOW",
            "severity": "NONE",
            "message": None,
            "resources": []
        },
    }

    # Lookup rule
    key = (category, risk_level)

    if key in rules:
        return rules[key]

    # Fallback for unhandled combinations
    return {
        "action": "FLAG_FOR_REVIEW",
        "severity": "UNKNOWN",
        "message": f"Unhandled case: {category}/{risk_level}. Needs human review.",
        "resources": []
    }