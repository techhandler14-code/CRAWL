"""
llm.py
 
Sets up the free Hugging Face LLM our agent will use to reason and decide
which tools to call.
 
Worth knowing upfront: Hugging Face's free tier is rate-limited (roughly
10 requests/minute with a token) and a model can take 30-60 seconds to
"wake up" on its very first call if it hasn't been used recently (called
a "cold start"). Since our ReAct agent makes one LLM call per
Thought/Action step (not just once per task), a single niche search might
involve several calls - so expect this to feel noticeably slower than a
paid API like GPT-4. This is the real trade-off of staying free, and
you'll feel it directly once we run the full agent - a good preview of
Module 6 (AgentExecutor limitations)."""


import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()
 
HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

MODEL_REPO_ID = "meta-llama/Llama-3.1-8B-Instruct"

def get_llm() -> ChatHuggingFace:
    """
    Returns a ready-to-use chat LLM, wired to our free Hugging Face model.
    This is what agent_executor.py will import and use.
    """
    # HuggingFaceEndpoint is the low-level connector - it just does raw
    # text generation.
    endpoint = HuggingFaceEndpoint(
        repo_id=MODEL_REPO_ID,
        task="text-generation",
        max_new_tokens=512,
        temperature=0.1,  # low temperature = more consistent, rule-following
                            # answers, which matters a lot for an agent that
                            # needs to follow a strict Thought/Action format
        huggingfacehub_api_token=HF_API_KEY,
        provider="auto",  # let Hugging Face pick an available hosting provider
    )
 
    # ChatHuggingFace wraps that raw text generator so it behaves like a
    # proper "chat model" - the format LangChain agents expect (messages
    # with roles: system/human/ai), instead of one raw block of text.
    return ChatHuggingFace(llm=endpoint)

# Quick manual test
if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke("2 Lines poem on cricket.")
    print(response.content)