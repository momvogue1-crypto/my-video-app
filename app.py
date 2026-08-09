import streamlit as st
import requests
import base64
from PIL import Image

# Page Setup
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

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("🔑 Enter Gemini / Google API Key:", type="password")
    
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

# Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Main AI Engine se powered hoon. Kuch bhi pochhein!"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Direct Google REST Call
def query_google_ai(api_key, prompt, image_file=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    parts = []
    if image_file:
        image_bytes = image_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        parts.append({
            "inline_data": {
                "mime_type": image_file.type,
                "data": base64_image
            }
        })
    
    parts.append({"text": prompt})
    payload = {"contents": [{"parts": parts}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in data:
            return f"⚠️ Google API Error: {data['error'].get('message', 'Invalid Key or Quota Limits')}"
        else:
            return "⚠️ Connection Error: Server did not respond correctly."
    except Exception as e:
        return f"⚠️ Network Error: {str(e)}"

# Input Logic
if user_prompt := st.chat_input("Ask AI anything..."):
    if not api_key:
        st.error("⚠️ Pehle Sidebar mein apni Key enter karein!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                reply = query_google_ai(api_key, user_prompt, uploaded_file)
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
