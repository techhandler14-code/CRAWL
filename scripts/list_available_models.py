"""
list_available_models.py

Asks Hugging Face directly which chat-capable models are actually
available to YOUR account right now, instead of guessing a model name
and hoping it works. Model availability on the free tier shifts often,
so this is the reliable way to pick one.

Run from project root with:
    python -m scripts.list_available_models
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

response = httpx.get(
    "https://router.huggingface.co/v1/models",
    headers={"Authorization": f"Bearer {HF_API_KEY}"},
    timeout=30,
)

response.raise_for_status()
data = response.json()

model_ids = [item["id"] for item in data.get("data", [])]

# Save the FULL list to a file, so you can search it yourself if needed
# (e.g. Ctrl+F for a specific model family) without flooding the terminal
with open("scripts/available_models_full_list.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(model_ids))
print(f"Saved full list of {len(model_ids)} models to scripts/available_models_full_list.txt\n")

# Filter down to ones that look like instruct/chat-tuned models - these
# are the ones actually suitable for an agent that needs to follow
# instructions and hold a conversation, not raw base/completion models
filtered = [
    model_id for model_id in model_ids
    if "instruct" in model_id.lower() or "chat" in model_id.lower()
]

print(f"Filtered down to {len(filtered)} instruct/chat-tuned models. Showing first 25:\n")
for model_id in filtered[:25]:
    print(f"  - {model_id}")

print("\nPick one of these (ideally a small one, e.g. 7B-9B parameters,")
print("from a well-known family like Qwen/Llama/Mistral) and set")
print("MODEL_REPO_ID to it in agent/llm.py")