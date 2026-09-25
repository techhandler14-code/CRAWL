"""
4_Agent_Assistant.py

A general chat interface to the full agent - type anything (find leads,
search existing leads, import a file) and the agent decides which tool(s)
to use, same as our terminal testing in Phase 6, but in the browser with
visible chat history.

Important honesty check, tying back to Module 4 (Memory): we only ever
built SHORT-TERM memory into the agent - the scratchpad that lets it
remember steps WITHIN one task. We never built LONG-TERM memory across
separate messages. So each message you send here is handled as a totally
independent task - the agent does NOT recall earlier messages in this
chat when reasoning about a new one. The chat history you see is for
YOUR reference only, not something the agent itself can see.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from utils.styling import inject_custom_css, render_sidebar_branding
from agent.agent_executor import get_agent_executor

st.set_page_config(page_title="Agent Assistant - Lead Extractor", page_icon="📍", layout="wide")
inject_custom_css()
render_sidebar_branding()

st.markdown("# Agent Assistant")
st.caption("Chat with the agent directly - find leads, search existing ones, or ask questions")

st.info(
    "Each message is handled independently - the agent doesn't remember "
    "earlier messages in this chat. Be specific in every request "
    "(e.g. repeat the city/niche each time, rather than saying 'the same as before').",
    icon="ℹ️",
)

# st.session_state persists data across reruns WITHIN one browser session.
# This matters because Streamlit re-runs this entire script top to bottom
# on every single interaction - without session_state, chat_history would
# reset to empty every time you sent a new message.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Redraw every past message on each rerun, so the conversation stays visible
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# st.chat_input renders a chat-style box pinned to the bottom of the page
user_input = st.chat_input("Ask the agent to find leads, search existing ones, or anything else...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            executor = get_agent_executor()
            result = executor.invoke({"input": user_input})
            response = result["output"]
        st.markdown(response)

    st.session_state.chat_history.append({"role": "assistant", "content": response})