import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# 1. SETUP: Use environment variable for API key
# Set it in .env file: GEMINI_API_KEY="your-api-key-here"
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("❌ ERROR: GEMINI_API_KEY environment variable not set!")
    print("   Add it to your .env file: GEMINI_API_KEY='your-api-key-here'")
    print("   Or set it with: export GEMINI_API_KEY='your-api-key-here'")
    exit(1)
genai.configure(api_key=API_KEY)

print("--- 🔍 DIAGNOSTIC START ---")

# 2. CHECK: What models can this key actually see?
print("\nChecking available models for your API key...")
try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            # display_name might not exist, so use getattr with fallback
            display_name = getattr(m, 'display_name', None) or getattr(m, 'displayName', None) or m.name
            print(f"✅ AVAILABLE: {m.name} ({display_name})")
    
    if not available_models:
        print("❌ NO MODELS FOUND. Your API key might be invalid or has no access.")

    # 3. TEST: Try to force a connection to Gemini 2.5 Flash
    target_model = "models/gemini-2.5-flash"
    
    if target_model in available_models:
        print(f"\n--- 🚀 TESTING CONNECTION TO {target_model} ---")
        model = genai.GenerativeModel(target_model)
        
        try:
            # We use a tiny prompt to minimize token load
            response = model.generate_content("Test. Just say hello.")
            print(f"🎉 SUCCESS! The model responded: {response.text}")
        except Exception as e:
            print(f"❌ CONNECTION FAILED: {e}")
            print("\n👉 DIAGNOSIS:")
            if "429" in str(e):
                print("   - REGIONAL OUTAGE: The model is valid, but the server is full.")
                print("   - FIX: Retry in 5 minutes or fallback to 'gemini-2.0-flash'.")
            elif "404" in str(e):
                print("   - MODEL NOT FOUND: Check if your API key has Vertex AI enabled.")
            else:
                print("   - UNKNOWN ERROR. Paste this log into the chat.")
    else:
        print(f"\n⚠️ WARNING: {target_model} is NOT in your available list.")
        print("   - This explains why it fails. You may need to enable it in Google Cloud Console.")

except Exception as e:
    print(f"\n❌ CRITICAL SCRIPT ERROR: {e}")

print("\n--- 🔍 DIAGNOSTIC END ---")
