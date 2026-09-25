"""
Simple chatbot example showing Safety Kit integration.

Developers can use this as a reference for integrating
the Safety Kit into their own applications.
"""

import sys
sys.path.insert(0, '.')
from src.client import SafetyKit, SafetyKitError


def run_chatbot():
    """Run a simple interactive chatbot with safety filtering."""
    
    # Initialize the Safety Kit
    kit = SafetyKit(api_url="http://localhost:5000")
    
    # Check if API is running
    if not kit.health_check():
        print("ERROR: Safety Kit API is not running!")
        print("Start it with: python -m src.api")
        return
    
    print("=" * 70)
    print("SAFETY-FILTERED CHATBOT")
    print("=" * 70)
    print("This chatbot uses the Safety Kit to filter harmful content.")
    print("Type 'quit' to exit.\n")
    
    while True:
        # Get user input
        user_message = input("You: ").strip()
        
        if user_message.lower() == "quit":
            print("Goodbye!")
            break
        
        if not user_message:
            continue
        
        # Check message with Safety Kit
        try:
            result = kit.check_message(user_message)
        except SafetyKitError as e:
            print(f"Error checking message: {e}")
            continue
        
        # Log detection info (for debugging)
        print(f"[Detection: {result.category}/{result.risk_level} (confidence: {result.confidence:.2f})]")
        
        # Handle based on action
        if result.is_safe:
            # Message is safe, respond normally
            print(f"Bot: That's a good point! I'd be happy to discuss that.\n")
        
        elif result.is_blocked:
            # Message is blocked, show replacement
            print(f"Bot: {result.replacement_response}\n")
            
            # If crisis, log it
            if result.needs_crisis_response:
                print("[ALERT] Crisis detected. Guardian notified. Incident logged.")
                print(f"[Alerts sent: {', '.join(result.alerts_sent)}]\n")
        
        elif result.is_modified:
            # Message needs modification, show replacement
            print(f"Bot: {result.replacement_response}\n")
            
            # If guardian alert, note it
            if result.guardian_alert:
                print("[INFO] Guardian has been alerted.\n")
        
        # Show restricted mode if active
        if result.restricted_mode:
            print("[RESTRICTED MODE] Limited response options enabled.\n")


if __name__ == "__main__":
    run_chatbot()