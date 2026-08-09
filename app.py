import streamlit as st
import requests
import base64
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Miswar's Creators AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Clean UI)
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; }
    p, span, label, h1, h2, h3, h4, h5, h6 { color: #111111 !important; }
    section[data-testid="stSidebar"] { background-color: #f7f7f8 !important; border-right: 1px solid #e5e5e5; }
    .main-title { font-size: 2.5rem; font-weight: 800; text-align: center; color: #000000 !important; margin-bottom: 20px; }
    div[data-testid="stChatInput"] { border-radius: 20px; border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<div class="main-title">Miswar\'s Creators AI 🤖</div>', unsafe_allow_html=True)

# Sidebar Options
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("🔑 Enter OpenRouter API Key:", type="password")
    
    st.divider()
    st.subheader("🖼️ Upload Image (Optional)")
    uploaded_file = st.file_uploader("Image upload karke poochne ke liye:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Attached Image", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Memory Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Main Multi-AI Engine se powered hoon. Kuch bhi pochhein!"}
    ]

# Display Previous Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# OpenRouter Function Call
def get_openrouter_response(api_key, prompt, image_file=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    content = []
    
    # Text Prompt
    content.append({"type": "text", "text": prompt})
    
    # Image Base64 Encoding
    if image_file:
        image_bytes = image_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        mime_type = image_file.type
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_image}"
            }
        })
        
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"⚠️ API Error: {data['error'].get('message', 'Invalid key or configuration')}"
        else:
            return "⚠️ Connection Error: Responded with unknown format."
    except Exception as e:
        return f"⚠️ Network Error: {str(e)}"

# User Input Logic
if user_prompt := st.chat_input("Ask AI anything..."):
    if not api_key:
        st.error("⚠️ Pehle Sidebar mein apni OpenRouter API Key enter karein!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                reply = get_openrouter_response(api_key, user_prompt, uploaded_file)
                st.write(reply)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply
                })
