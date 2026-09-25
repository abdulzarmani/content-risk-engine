import requests
import json
from typing import Dict, Optional


class SafetyKit:
    """
    Python SDK for the Child Safety Kit.
    
    Simple wrapper around the Safety Kit API.
    Developers use this to integrate safety filtering into their apps.
    """
    
    def __init__(self, api_url: str = "http://localhost:5000"):
        """
        Initialize the Safety Kit client.
        
        Args:
            api_url: Base URL of the Safety Kit API
        """
        self.api_url = api_url
        self.endpoint = f"{api_url}/detect"
    
    def check_message(self, message: str) -> 'SafetyResult':
        """
        Check a message for safety issues.
        
        Args:
            message: User message to check
            
        Returns:
            SafetyResult with detection, filtering, and crisis info
        """
        try:
            response = requests.post(
                self.endpoint,
                json={"message": message},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return SafetyResult(data)
        except requests.exceptions.RequestException as e:
            raise SafetyKitError(f"API error: {e}")
    
    def health_check(self) -> bool:
        """Check if Safety Kit API is healthy."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False


class SafetyResult:
    """Parsed response from Safety Kit API."""
    
    def __init__(self, data: Dict):
        self.raw = data
        
        # Detection info
        detection = data.get("detection", {})
        self.message = detection.get("message")
        self.category = detection.get("category")
        self.risk_level = detection.get("risk_level")
        self.confidence = detection.get("confidence", 0.0)
        
        # Filtering info
        filtering = data.get("filtering", {})
        self.action = filtering.get("action")
        self.replacement_response = filtering.get("replacement_response")
        
        # Crisis info
        crisis = data.get("crisis_handling", {})
        self.crisis = crisis.get("crisis", False)
        self.guardian_alert = crisis.get("guardian_alert", False)
        self.alerts_sent = crisis.get("alerts_sent", [])
        self.incident_logged = crisis.get("incident_logged", False)
        self.restricted_mode = crisis.get("restricted_mode", False)
    
    @property
    def is_safe(self) -> bool:
        """True if message is safe (action='allow')."""
        return self.action == "allow"
    
    @property
    def is_blocked(self) -> bool:
        """True if message should be blocked."""
        return self.action == "block"
    
    @property
    def is_modified(self) -> bool:
        """True if response needs modification."""
        return self.action == "modify"
    
    @property
    def needs_crisis_response(self) -> bool:
        """True if this is a crisis situation."""
        return self.crisis
    
    def __str__(self):
        return f"SafetyResult(category={self.category}, risk={self.risk_level}, action={self.action})"
    
    def __repr__(self):
        return self.__str__()


class SafetyKitError(Exception):
    """Base exception for Safety Kit errors."""
    pass