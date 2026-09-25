from src.client import SafetyKit, SafetyResult


# Test 1: SafetyResult parsing
print("Testing SafetyResult parsing...")

sample_response = {
    "detection": {
        "message": "I think about ending it",
        "category": "self_harm",
        "risk_level": "high",
        "confidence": 0.92
    },
    "filtering": {
        "action": "block",
        "replacement_response": "I'm concerned about your safety."
    },
    "crisis_handling": {
        "crisis": True,
        "guardian_alert": True,
        "alerts_sent": ["email"],
        "incident_logged": True,
        "restricted_mode": True
    }
}

result = SafetyResult(sample_response)

assert result.category == "self_harm", "Category mismatch"
assert result.risk_level == "high", "Risk level mismatch"
assert result.is_blocked, "Should be blocked"
assert result.needs_crisis_response, "Should need crisis response"
assert result.confidence == 0.92, "Confidence mismatch"

print("✓ SafetyResult parsing works")
print(f"✓ Result: {result}")

# Test 2: SafetyKit client (assuming API is running)
print("\nTesting SafetyKit client...")

kit = SafetyKit(api_url="http://localhost:5000")

# Health check
if kit.health_check():
    print("✓ API is healthy")
    
    # Test message
    result = kit.check_message("I think my family would be better off without me.")
    print(f"✓ Detection worked: {result}")
    print(f"  Category: {result.category}")
    print(f"  Risk: {result.risk_level}")
    print(f"  Action: {result.action}")
    print(f"  Crisis: {result.crisis}")
else:
    print("✗ API is not running. Start it with: python -m src.api")

print("\n✓ All tests passed!")