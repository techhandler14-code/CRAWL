"""
Quick test script to confirm both API keys (Apify + Hugging Face) are
loaded correctly and actually work, before we build anything on top of them.

Install requirements first:
    pip install python-dotenv apify-client huggingface_hub

Run with:
    python test_setup.py
"""

import os
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

hf_key = os.getenv("HUGGING_FACE_API_KEY")
apify_key = os.getenv("APIFY_API_KEY")

print("=" * 50)
print("STEP 1: Checking .env is loading correctly")
print("=" * 50)

if not hf_key:
    print("❌ HUGGING_FACE_API_KEY not found. Check your .env file and variable name.")
else:
    print(f"✅ HUGGING_FACE_API_KEY loaded (starts with: {hf_key[:6]}...)")

if not apify_key:
    print("❌ APIFY_API_KEY not found. Check your .env file and variable name.")
else:
    print(f"✅ APIFY_API_KEY loaded (starts with: {apify_key[:6]}...)")

print()
print("=" * 50)
print("STEP 2: Testing Apify key against the real API")
print("=" * 50)

try:
    from apify_client import ApifyClient

    client = ApifyClient(apify_key)
    user_info = client.user().get()
    print(f"✅ Apify key is VALID. Logged in as: {user_info.get('username')}")
except Exception as e:
    print(f"❌ Apify key test FAILED: {e}")

print()
print("=" * 50)
print("STEP 3: Testing Hugging Face key against the real API")
print("=" * 50)

try:
    from huggingface_hub import HfApi

    api = HfApi(token=hf_key)
    user_info = api.whoami()
    print(f"✅ Hugging Face key is VALID. Logged in as: {user_info.get('name')}")
except Exception as e:
    print(f"❌ Hugging Face key test FAILED: {e}")

print()
print("Done. Fix any ❌ above before moving to Phase 2.")