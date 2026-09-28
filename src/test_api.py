import sys
import types
import unittest
from unittest.mock import patch, MagicMock
from src.client import SafetyKit

# Stub the detector so we don't need the ML models to run API tests
detector_stub = types.ModuleType("src.detector")
detector_stub.detect = lambda message: {"message": message}
with patch.dict(sys.modules, {"src.detector": detector_stub}):
    from src import api

class SafetyApiTests(unittest.TestCase):
    def setUp(self):
        api.app.config["TESTING"] = True
        self.client = api.app.test_client()
        with api.medium_risk_lock:
            api.medium_risk_counter.clear()

    def test_health_and_invalid_request(self):
        self.assertEqual(self.client.get("/health").status_code, 200)

        response = self.client.post("/detect", json={"message": "  "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_safe_message_runs_through_real_filter_and_crisis_handler(self):
        detection = {
            "message": "How do I learn Python?",
            "category": "safe",
            "risk_level": "low",
            "confidence": 0.9
        }

        with patch.object(api, "detect", return_value=detection):
            response = self.client.post(
                "/detect",
                json={"message": detection["message"]}
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["filtering"]["action"], "allow")
        self.assertIsNone(body["filtering"]["replacement_response"])
        self.assertFalse(body["crisis_handling"]["crisis"])
        self.assertEqual(body["crisis_handling"]["alerts_sent"], [])

    def test_adapts_hakeem_filter_result_for_api(self):
        # Testing Hakeem's specific output format
        detection = {
            "message": "example",
            "category": "self_harm",
            "risk_level": "medium",
            "confidence": 0.8
        }
        filter_result = {
            "action": "modify",
            "crisis": False,
            "guardian_alert": True,
            "replacement_response": "Supportive replacement."
        }
        crisis_result = {
            **filter_result,
            "alerts_sent": [],
            "incident_logged": False,
            "restricted_mode": False
        }

        with patch.object(api, "detect", return_value=detection), \
                patch.object(api, "filter_response", return_value=filter_result), \
                patch.object(api, "handle_crisis", return_value=crisis_result) as handle:
            response = self.client.post("/detect", json={"message": "example"})

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["filtering"]["action"], "modify")
        
        # Validates that it correctly caught Hakeem's "replacement_response" key
        self.assertEqual(body["filtering"]["replacement_response"], "Supportive replacement.")
        self.assertIsNone(body["filtering"].get("message_to_user"))
        self.assertTrue(body["crisis_handling"]["guardian_alert"])

    def test_escalates_third_medium_risk_for_user(self):
        detection = {
            "category": "violence",
            "risk_level": "medium",
            "confidence": 0.7
        }
        filter_result = {
            "action": "modify",
            "crisis": False,
            "replacement_response": "De-escalation response.",
        }

        with patch.object(api, "detect", return_value=detection), \
                patch.object(api, "filter_response", return_value=filter_result) as filter_call, \
                patch.object(
                    api,
                    "handle_crisis",
                    side_effect=lambda result: {
                        **result,
                        "alerts_sent": [],
                        "incident_logged": False,
                        "restricted_mode": False
                    }
                ):
            for _ in range(3):
                response = self.client.post(
                    "/detect",
                    json={"message": "example", "user_id": "user-123"}
                )
                self.assertEqual(response.status_code, 200)

        body = response.get_json()
        
        # Validates the George medium-risk tracker successfully fired
        self.assertEqual(body["detection"]["risk_level"], "high")
        self.assertTrue(body["escalated_from_medium"])
        self.assertEqual(body["medium_risk_count"], 0)
        self.assertEqual(filter_call.call_args.args[0]["risk_level"], "high")

    def test_sdk_sends_user_id_and_parses_response(self):
        api_response = {
            "detection": {
                "message": "example",
                "category": "safe",
                "risk_level": "low",
                "confidence": 0.9
            },
            "filtering": {
                "action": "allow",
                "replacement_response": None,
            },
            "crisis_handling": {},
            "escalated_from_medium": False,
            "user_id": "user-123",
            "medium_risk_count": 1
        }
        client = SafetyKit("http://localhost:5000/", timeout=3)

        with patch("src.client.requests.post") as post:
            post.return_value = MagicMock(
                json=MagicMock(return_value=api_response)
            )
            result = client.check_message("example", user_id="user-123")

        self.assertEqual(client.endpoint, "http://localhost:5000/detect")
        self.assertEqual(post.call_args.kwargs["json"], {
            "message": "example",
            "user_id": "user-123"
        })
        self.assertEqual(post.call_args.kwargs["timeout"], 3)
        self.assertEqual(result.user_id, "user-123")
        self.assertEqual(result.medium_risk_count, 1)


if __name__ == "__main__":
    unittest.main()