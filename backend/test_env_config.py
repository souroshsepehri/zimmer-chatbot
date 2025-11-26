#!/usr/bin/env python3
"""Test script to verify .env file is being loaded correctly"""

from core.config import settings

print("=" * 50)
print("Environment Configuration Test")
print("=" * 50)
print()

# Check API Key
api_key_loaded = bool(settings.openai_api_key and settings.openai_api_key != "")
print(f"✓ API Key: {'LOADED' if api_key_loaded else 'MISSING'}")
if api_key_loaded:
    print(f"  Length: {len(settings.openai_api_key)} characters")
    print(f"  Starts with: {settings.openai_api_key[:10]}...")

print()

# Check Model Configuration
print(f"✓ Model: {settings.openai_model}")
print(f"✓ Embedding Model: {settings.embedding_model}")

print()

# Check Other Settings
print("Other Settings:")
print(f"  - Server Port: {settings.server_port}")
print(f"  - Server Host: {settings.server_host}")
print(f"  - Database: {settings.database_url}")
print(f"  - Retrieval Top K: {settings.retrieval_top_k}")
print(f"  - Retrieval Threshold: {settings.retrieval_threshold}")

print()
print("=" * 50)
if api_key_loaded:
    print("✅ SUCCESS: .env file is working correctly!")
    print("   Your chatbot is ready to use GPT-3.5 Turbo with your API key.")
else:
    print("⚠️  WARNING: API key not found in .env file")
    print("   Please check your .env file in the backend directory.")
print("=" * 50)






