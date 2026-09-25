"""
agent_executor.py

This is where everything we've built comes together into one real,
working agent. It wires up:
  - the LLM (agent/llm.py)
  - the ReAct prompt (agent/prompts.py)
  - the tools the agent is allowed to use

Running this file gives you a live AgentExecutor you can hand a task to,
in plain English, and watch it reason through Thought -> Action ->
Observation on its own - the full Module 1-4 mental model, actually running.
"""

from langchain.agents import AgentExecutor, create_structured_chat_agent

from agent.llm import get_llm
from agent.prompts import STRUCTURED_CHAT_PROMPT
from tools.apify_maps_tool import extract_leads_tool
from tools.search_leads_tool import search_leads_tool, list_niches_tool
from tools.import_leads_tool import import_leads_tool

# Every tool the agent is allowed to call. Order doesn't matter - the LLM
# picks based on the tool names/descriptions injected into the prompt.
TOOLS = [extract_leads_tool, search_leads_tool, list_niches_tool, import_leads_tool]


def get_agent_executor() -> AgentExecutor:
    """
    Builds and returns a ready-to-use AgentExecutor.
    Other files (like the Streamlit dashboard) will import this function
    rather than duplicating this setup.
    """
    llm = get_llm()

    # create_structured_chat_agent wires the LLM + prompt + tools together,
    # using JSON-formatted actions so multi-argument tools work correctly.
    agent = create_structured_chat_agent(llm=llm, tools=TOOLS, prompt=STRUCTURED_CHAT_PROMPT)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,              # prints every Thought/Action/Observation live
        handle_parsing_errors=True, # if the LLM's output doesn't match our
                                     # strict format, retry instead of crashing
        max_iterations=6,           # safety limit - stop after 6 loops even
                                     # if the agent never says "Final Answer"
        return_intermediate_steps=True,  # gives us access to each tool's
                                          # actual return value, not just the
                                          # LLM's final text summary - the
                                          # dashboard will use this for
                                          # accurate, real numbers
    )


# Manual test - give the agent a real task and watch it work
if __name__ == "__main__":
    executor = get_agent_executor()
    result = executor.invoke({
        "input": "Find electricians in Lahore with no website."
    })
    print("\n\nFINAL RESULT:")
    print(result["output"])