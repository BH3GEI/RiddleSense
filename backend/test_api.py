import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def test_gemini_api():
    """Test function to make a simple call to the Gemini API"""
    
    url = f"{BASE_URL}?key={API_KEY}"
    
    # Simple payload for testing
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Please respond with a simple JSON: {\"test\": \"successful\"}"}]
            }
        ]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("Making API call...")
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error response:")
        print(response.text)
    
    return response

if __name__ == "__main__":
    test_gemini_api()
