#!/usr/bin/env python3
"""Simple test using requests to verify Gemini API key."""

import requests
import json

api_key = "AIzaSyB3Vu98aOmYOxPLUrvHMxhPAknz78scNcs"

# First, try to list available models to verify the API key works
print("Step 1: Checking available models...")
list_models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    models_response = requests.get(list_models_url, timeout=10)
    models_response.raise_for_status()
    models_data = models_response.json()
    
    # Find a model that supports generateContent
    available_models = []
    if "models" in models_data:
        for model in models_data["models"]:
            if "generateContent" in model.get("supportedGenerationMethods", []):
                model_name = model["name"].split("/")[-1]
                available_models.append(model_name)
                print(f"  Found model: {model_name}")
    
    if not available_models:
        print("  ⚠️  No models found that support generateContent")
        # Try common model names
        available_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    # Use the first available model or a common one
    model_name = available_models[0] if available_models else "gemini-1.5-flash"
    print(f"\nStep 2: Testing with model: {model_name}")
    
except Exception as e:
    print(f"  ⚠️  Could not list models: {e}")
    print("  Will try with common model names...")
    model_name = "gemini-1.5-flash"

# Now test generateContent
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [{
        "parts": [{
            "text": "Say 'Hello, API test successful!' in exactly those words."
        }]
    }]
}

print("Testing Gemini API connection...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    response.raise_for_status()
    
    result = response.json()
    if "candidates" in result and len(result["candidates"]) > 0:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        print(f"\n✅ API Key is working!")
        print(f"Response: {text}")
    else:
        print(f"\n⚠️  Unexpected response format:")
        print(json.dumps(result, indent=2))
        
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print(f"\n❌ API Key is invalid or expired (401 Unauthorized)")
    elif e.response.status_code == 429:
        print(f"\n⚠️  Rate limit exceeded (429). The key works but you've hit the limit.")
    else:
        print(f"\n❌ HTTP Error {e.response.status_code}: {e}")
        try:
            print(f"Response: {e.response.text}")
        except:
            pass
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
