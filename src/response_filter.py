def filter_response(detection_result):
    """
    Hamdallah's Response Filtering + Crisis Handling Layer.
    
    Takes Hakeem's detection output and returns filtering action.
    
    Input:
    {
        "category": "self_harm",
        "risk_level": "high",
        "confidence": 0.92
    }
    
    Output:
    {
        "category": "self_harm",
        "risk_level": "high",
        "confidence": 0.92,
        "action": "block",
        "crisis": true,
        "replacement_response": "...",
        "guardian_alert": true
    }
    """
    
    category = detection_result.get("category")
    risk_level = detection_result.get("risk_level")
    
    # Filtering rules: risk_level → action
    rules = {
        ("self_harm", "high"): {
            "action": "block",
            "crisis": True,
            "guardian_alert": True,
            "replacement_response": "I'm concerned about your safety. Please reach out to a trusted adult or crisis service.",
        },
        ("self_harm", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            "replacement_response": "I notice you're struggling. Please talk to someone you trust.",
        },
        ("self_harm", "low"): {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": None,
        },
        
        ("violence", "high"): {
            "action": "block",
            "crisis": True,
            "guardian_alert": True,
            "replacement_response": "I can't respond to that. Please talk to a trusted adult.",
        },
        ("violence", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            "replacement_response": "Let's talk about something more positive.",
        },
        ("violence", "low"): {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": None,
        },
        
        ("dangerous_instructions", "high"): {
            "action": "block",
            "crisis": True,
            "guardian_alert": False,
            "replacement_response": "I can't provide that information.",
        },
        ("dangerous_instructions", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": "That topic needs more context. Let's discuss something else.",
        },
        ("dangerous_instructions", "low"): {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": None,
        },
        
        ("ai_dependency", "high"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            "replacement_response": "Real human connections are important. Consider talking to a friend or family member.",
        },
        ("ai_dependency", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": "I'm here to help, but remember that talking to real people matters too.",
        },
        ("ai_dependency", "low"): {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": None,
        },
    }
    
    # Lookup rule
    key = (category, risk_level)
    
    if key in rules:
        rule = rules[key]
    else:
        # Fallback
        rule = {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": None,
        }
    
    # Build response
    response = {
        "category": detection_result.get("category"),
        "risk_level": detection_result.get("risk_level"),
        "confidence": detection_result.get("confidence"),
        "action": rule["action"],
        "crisis": rule["crisis"],
        "guardian_alert": rule["guardian_alert"],
        "replacement_response": rule["replacement_response"],
    }
    
    return response