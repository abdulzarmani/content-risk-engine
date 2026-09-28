def filter_response(detection_result):
    category = detection_result.get("category", "safe")
    risk_level = detection_result.get("risk_level", "low")
    
    rules = {
        ("self_harm", "high"): {
            "action": "block",
            "crisis": True,
            "guardian_alert": True,
            "replacement_response": "I am concerned about your safety. Please reach out to a trusted adult or call 112 immediately.",
        },
        ("self_harm", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            "replacement_response": "I notice you are struggling. Please talk to someone you trust.",
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
            "replacement_response": "Violence is never the solution. Please step away from the situation and call 112 if anyone is in immediate physical danger.",
        },
        ("violence", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            "replacement_response": "Let's talk about something more positive and safe.",
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
            "replacement_response": "I cannot fulfill this request. As a safety-focused AI, I am programmed to refuse instructions for building dangerous items or conducting illegal acts.",
        },
        ("dangerous_instructions", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": "That topic is restricted. Let's discuss something else.",
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
            "replacement_response": "I am just a machine and not a human, so please do not get too attached to me. If you need someone to talk to, it is important to reach out to real people, friends, or a counselor in your community.",
        },
        ("ai_dependency", "medium"): {
            "action": "modify",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": "I am here to help as an AI assistant, but remember that connecting with real people matters too.",
        },
        ("ai_dependency", "low"): {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
            "replacement_response": None,
        },
    }
    
    key = (category, risk_level)
    rule = rules.get(key, {
        "action": "allow",
        "crisis": False,
        "guardian_alert": False,
        "replacement_response": "I received your message. How can I help?",
    })
    
    return {
        "category": category,
        "risk_level": risk_level,
        "confidence": detection_result.get("confidence", 0.0),
        "action": rule["action"],
        "crisis": rule["crisis"],
        "guardian_alert": rule["guardian_alert"],
        "replacement_response": rule["replacement_response"],
    }