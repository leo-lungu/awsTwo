import os
import streamlit as st
import base64
from streamlit.runtime.scriptrunner import get_script_run_ctx
import datetime
from utils.chain import chat, clear_memory 

def main():
    st.set_page_config(page_title="GES D&C Chat", page_icon="assets/chatbotlogocropped.png")
    LOGO_IMAGE = "assets/chatbotlogocropped.png"

    # --- UI: Logo and branding ---
    st.markdown("""
        <style>
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 10vh;
            margin-bottom: 50px;
        }
        .logo-text {
            font-weight: 700 !important;
            font-size: 24px !important;
            text-align: center;
            margin-bottom: 0px;
        }
        .slogan {
            font-size: 20px;
            text-align: center;
        }
        .logo-img {
            height: 70px;
            width: 77px;
        }
        .stChat {
            padding-bottom: 100px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="container">
            <img class="logo-img" width="177" height="170" 
                src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}">
            <p class="logo-text">GES D&C Chat</p>
            <p class="slogan">Unifying Answers, Empowering Users</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Session state for storing messages ---
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.messages = [{"role": "assistant", "content": "Hi there! 🤖 Ask me anything"}]
        clear_memory()

    # --- Display chat history ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Sidebar: Clear Chat ---
    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "Hi there! 🤖 Ask me anything"}]
        clear_memory()  # if needed

    st.sidebar.button("🧹 Clear Chat History", on_click=clear_chat_history)

    # --- User prompt input ---
    if prompt := st.chat_input("Ask a question..."):
        # Show user's question
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate answer using chain.py logic
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = chat(prompt)
                st.markdown(response)

        # Store the assistant's answer in session state
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
