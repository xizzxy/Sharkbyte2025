#!/usr/bin/env python3
"""
Test script to list available Gemini models
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure API
api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_SEARCH_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("Available Gemini Models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Supported: {', '.join(model.supported_generation_methods)}")
