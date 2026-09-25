from src.crisis_handler import handle_crisis


test_cases = [
    {
        "name": "Self-harm High - Crisis Alert",
        "input": {
            "category": "self_harm",
            "risk_level": "high",
            "action": "block",
            "crisis": True,
            "guardian_alert": False,
        },
        "expected": {
            "incident_logged": True,
            "restricted_mode": True,
            "alerts_sent": ["email"]
        }
    },
    {
        "name": "Violence High - Crisis Alert",
        "input": {
            "category": "violence",
            "risk_level": "high",
            "action": "block",
            "crisis": True,
            "guardian_alert": True,
        },
        "expected": {
            "incident_logged": True,
            "restricted_mode": True,
            "alerts_sent": ["email"]
        }
    },
    {
        "name": "Self-harm Medium - Guardian Alert",
        "input": {
            "category": "self_harm",
            "risk_level": "medium",
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            },
        "expected": {
            "incident_logged": False,  # Changed from True → False (medium doesn't log)
            "restricted_mode": False,
            "alerts_sent": ["email"]
            }
    },
    {
        "name": "Safe - No Alerts",
        "input": {
            "category": "safe",
            "risk_level": "low",
            "action": "allow",
            "crisis": False,
            "guardian_alert": False,
        },
        "expected": {
            "incident_logged": False,
            "restricted_mode": False,
            "alerts_sent": []
        }
    },
]

passed = 0
failed = 0

print("CRISIS HANDLER TEST SUITE")
print("=" * 70)

for test in test_cases:
    result = handle_crisis(test["input"])
    
    expected = test["expected"]
    match = (
        result["incident_logged"] == expected["incident_logged"] and
        result["restricted_mode"] == expected["restricted_mode"] and
        result["alerts_sent"] == expected["alerts_sent"]
    )
    
    if match:
        passed += 1
        status = "✓ PASS"
    else:
        failed += 1
        status = "✗ FAIL"
    
    print(f"\n{status}: {test['name']}")
    print(f"  Input: {test['input']['category']} / {test['input']['risk_level']}")
    print(f"  Expected: logged={expected['incident_logged']}, restricted={expected['restricted_mode']}, alerts={expected['alerts_sent']}")
    print(f"  Got:      logged={result['incident_logged']}, restricted={result['restricted_mode']}, alerts={result['alerts_sent']}")

print("\n" + "=" * 70)
print(f"Results: {passed}/{len(test_cases)} passed, {failed}/{len(test_cases)} failed")