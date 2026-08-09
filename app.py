import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. Page Configuration
st.set_page_config(
    page_title="Miswar's Creators AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; }
    p, span, label, h1, h2, h3, h4, h5, h6 { color: #111111 !important; }
    section[data-testid="stSidebar"] { background-color: #f7f7f8 !important; border-right: 1px solid #e5e5e5; }
    .main-title { font-size: 2.5rem; font-weight: 800; text-align: center; color: #000000 !important; margin-bottom: 20px; }
    div[data-testid="stChatInput"] { border-radius: 20px; border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Miswar\'s Creators AI 🤖</div>', unsafe_allow_html=True)

# 2. Sidebar Setup
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("🔑 Enter Gemini API Key:", type="password")
    
    st.divider()
    st.subheader("🖼️ Upload Image (Optional)")
    uploaded_file = st.file_uploader("Image ke bare mein poochne ke liye:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Attached Image", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. Chat Session Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Main Google Gemini AI se powered hoon. Kuch bhi pochhein!"}
    ]

# Display Existing Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to call Gemini REST API directly
def call_gemini_api(api_key, prompt, image_file=None):
    # Standard endpoints list to try automatically
    models_to_try = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-pro"
    ]
    
    parts = []
    
    # If image is attached, convert to Base64
    if image_file:
        image_bytes = image_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        mime_type = image_file.type
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": base64_image
            }
        })
    
    parts.append({"text": prompt})
    payload = {"contents": [{"parts": parts}]}
    
    last_error = ""
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, timeout=30)
            data = res.json()
            
            if res.status_code == 200 and "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in data:
                last_error = data["error"].get("message", "Unknown error")
                if "429" in str(res.status_code) or "RESOURCE_EXHAUSTED" in last_error:
                    return "⏳ **Rate Limit Hit**: Google API per free quota complete ho gaya hai. Please 30 seconds wait karke try karein ya naye Google account se API Key banayein."
        except Exception as e:
            last_error = str(e)
            
    return f"⚠️ Error: {last_error}"

# 4. User Chat Input Logic
if user_prompt := st.chat_input("Ask Gemini anything..."):
    if not api_key:
        st.error("⚠️ Pehle Sidebar mein apni Gemini API Key enter karein!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Miswar's AI is thinking..."):
                response_text = call_gemini_api(api_key, user_prompt, uploaded_file)
                st.write(response_text)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text
                })
