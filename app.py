# app.py
import re

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

# Import the agent initializer from its new location
from agent.agent import initialize_agent

def extract_image_paths(text: str) -> list[str]:
    """
    Finds all image filenames (png/jpeg) in a block of text,
    whether in quotes or bare.
    """
    return re.findall(r"['\"]?([A-Za-z0-9_\-]+\.(?:png|jpg|jpeg))['\"]?", text)


st.set_page_config(page_title="🤖 Smart Financial Analytics Agent", layout="wide")
st.title("🤖 CFO Copilot")

# Initialize the agent
agent_executor = initialize_agent()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):

        st.text(message["content"])
        if "image_path" in message and message["image_path"]:
            st.image(message["image_path"])

# Get user input
if prompt := st.chat_input("Ask a question about your financial data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chat_history = [
                HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
                for msg in st.session_state.messages[:-1]
            ]

            response = agent_executor.invoke({
                "input": prompt,
                "chat_history": chat_history
            })

            output_text = response["output"]
            st.text(output_text)

            # Collect any image paths from intermediate steps & output
            image_paths = []

            # 1. From intermediate_steps (even if action.tool != 'plot_chart')
            for step in response.get("intermediate_steps", []):
                _, observation = step
                # observation might be a filename or a descriptive text
                if isinstance(observation, str):
                    image_paths += extract_image_paths(observation)

            # 2. From the assistant’s final output text
            image_paths += extract_image_paths(output_text)

            # 3. De-duplicate and display
            for path in dict.fromkeys(image_paths):  # preserves order, removes dups
                try:
                    st.image(path)
                    # also record for session state
                    image_path = path
                except Exception as e:
                    st.error(f"Failed to load image {path}: {e}")

            # Save session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": output_text,
                "image_path": image_path if image_paths else None
            })
