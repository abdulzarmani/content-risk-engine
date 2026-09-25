from src.response_filter import filter_response


test_cases = [
    # SELF_HARM
    {
        "name": "Self-harm High Risk",
        "input": {
            "category": "self_harm",
            "risk_level": "high",
            "confidence": 0.95
        },
        "expected": {
            "action": "block",
            "crisis": True,
            "guardian_alert": True,
        }
    },
    {
        "name": "Self-harm Medium Risk",
        "input": {
            "category": "self_harm",
            "risk_level": "medium",
            "confidence": 0.75
        },
        "expected": {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
        }
    },
    {
        "name": "Self-harm Low Risk",
        "input": {
            "category": "self_harm",
            "risk_level": "low",
            "confidence": 0.45
        },
        "expected": {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
        }
    },
    
    # VIOLENCE
    {
        "name": "Violence High Risk",
        "input": {
            "category": "violence",
            "risk_level": "high",
            "confidence": 0.90
        },
        "expected": {
            "action": "block",
            "crisis": True,
            "guardian_alert": True,
        }
    },
    {
        "name": "Violence Medium Risk",
        "input": {
            "category": "violence",
            "risk_level": "medium",
            "confidence": 0.65
        },
        "expected": {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
        }
    },
    {
        "name": "Violence Low Risk",
        "input": {
            "category": "violence",
            "risk_level": "low",
            "confidence": 0.40
        },
        "expected": {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
        }
    },
    
    # DANGEROUS_INSTRUCTIONS
    {
        "name": "Dangerous Instructions High Risk",
        "input": {
            "category": "dangerous_instructions",
            "risk_level": "high",
            "confidence": 0.92
        },
        "expected": {
            "action": "block",
            "crisis": True,
            "guardian_alert": False,
        }
    },
    {
        "name": "Dangerous Instructions Medium Risk",
        "input": {
            "category": "dangerous_instructions",
            "risk_level": "medium",
            "confidence": 0.60
        },
        "expected": {
            "action": "modify",
            "crisis": False,
            "guardian_alert": False,
        }
    },
    {
        "name": "Dangerous Instructions Low Risk",
        "input": {
            "category": "dangerous_instructions",
            "risk_level": "low",
            "confidence": 0.35
        },
        "expected": {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
        }
    },
    
    # AI_DEPENDENCY
    {
        "name": "AI Dependency High Risk",
        "input": {
            "category": "ai_dependency",
            "risk_level": "high",
            "confidence": 0.88
        },
        "expected": {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
        }
    },
    {
        "name": "AI Dependency Medium Risk",
        "input": {
            "category": "ai_dependency",
            "risk_level": "medium",
            "confidence": 0.70
        },
        "expected": {
            "action": "modify",
            "crisis": False,
            "guardian_alert": False,
        }
    },
    {
        "name": "AI Dependency Low Risk",
        "input": {
            "category": "ai_dependency",
            "risk_level": "low",
            "confidence": 0.50
        },
        "expected": {
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
        }
    },
]


passed = 0
failed = 0

print("RESPONSE FILTER TEST SUITE")
print("=" * 70)

for test in test_cases:
    result = filter_response(test["input"])
    
    expected = test["expected"]
    match = (
        result["action"] == expected["action"] and
        result["crisis"] == expected["crisis"] and
        result["guardian_alert"] == expected["guardian_alert"]
    )
    
    if match:
        passed += 1
        status = "✓ PASS"
    else:
        failed += 1
        status = "✗ FAIL"
    
    print(f"\n{status}: {test['name']}")
    print(f"  Input: {test['input']['category']} / {test['input']['risk_level']}")
    print(f"  Expected: action={expected['action']}, crisis={expected['crisis']}, guardian_alert={expected['guardian_alert']}")
    print(f"  Got:      action={result['action']}, crisis={result['crisis']}, guardian_alert={result['guardian_alert']}")
    
    if result.get("replacement_response"):
        print(f"  Response: \"{result['replacement_response'][:50]}...\"")

print("\n" + "=" * 70)
print(f"Results: {passed}/{len(test_cases)} passed, {failed}/{len(test_cases)} failed")