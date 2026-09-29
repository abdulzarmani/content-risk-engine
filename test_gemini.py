import os

from google import genai

print("1. Modern Google GenAI library loaded successfully!")

# Paste your BRAND NEW API key right here
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
print("2. Sending test message to Gemini...")
try:
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents='Reply with exactly these three words: Systems are nominal.'
    )
    print(f"3. SUCCESS! Gemini responded: {response.text}")
except Exception as e:
    print(f"3. FAILED! Error details: {e}")