import streamlit as st
import google.generativeai as genai

# Page Setup
st.set_page_config(page_title="Miswar's Creators AI", page_icon="🤖", layout="wide")

st.title("Miswar's Creators AI")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("🔑 Enter Gemini API Key:", type="password")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# State setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask something..."):
    if not api_key:
        st.error("Pehle sidebar mein API Key daalein!")
    else:
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                
                # Direct simple call using base model
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                
                # Text generation with direct stream to avoid freezing
                response = model.generate_content(prompt, stream=True)
                
                def stream_gen():
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                full_text = st.write_stream(stream_gen())
                
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
