import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

print("Testing models...")
print("=" * 60)

# Test 1: List models
print("\n1. Available models with generateContent:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"   ✅ {m.name}")

# Test 2: Try generating with different model names
test_models = [
    "models/gemini-pro",
    "gemini-pro",
    "models/gemini-1.5-flash-latest",
    "gemini-1.5-flash-latest"
]

print("\n2. Testing generation with different model names:")
for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'test successful'")
        print(f"   ✅ {model_name}: {response.text[:50]}")
        break  # Stop on first success
    except Exception as e:
        print(f"   ❌ {model_name}: {str(e)[:80]}")
