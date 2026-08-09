import streamlit as st
import google.generativeai as genai
from PIL import Image

# Page Setup
st.set_page_config(
    page_title="Miswar's Creators - Powered by Gemini",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Clean Light Theme (Black & White)
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; }
    p, span, label, h1, h2, h3, h4, h5, h6 { color: #111111 !important; }
    section[data-testid="stSidebar"] { background-color: #f7f7f8 !important; border-right: 1px solid #e5e5e5; }
    .chatgpt-header { text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid #eaeaea; margin-bottom: 15px; }
    .main-title { font-size: 2.5rem; font-weight: 800; color: #000000 !important; }
    div[data-testid="stChatInput"] { border-radius: 20px; border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="chatgpt-header">
    <div class="main-title">Miswar's Creators AI</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Options
with st.sidebar:
    st.title("⚙️ Gemini Settings")
    
    # Enter API Key
    api_key = st.text_input("🔑 Enter Gemini API Key:", type="password")
    
    st.divider()
    
    # Image Upload (Vision Input)
    st.subheader("🖼️ Upload Image (Optional)")
    uploaded_file = st.file_uploader("Image upload karke kuch bhi pochein:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Attached Image", use_container_width=True)
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Main Google Gemini AI se powered hoon. Aap mujh se koi bhi sawal pooch sakte hain ya image upload karke uske bare mein jaan sakte hain."}
    ]

# Display Existing Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_prompt := st.chat_input("Ask Gemini anything..."):
    if not api_key:
        st.error("⚠️ Pehle Sidebar mein apni Gemini API Key daalein!")
    else:
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate Response using Gemini
        with st.chat_message("assistant"):
            with st.spinner("Gemini is thinking..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # Choose model: if image uploaded, use vision multimodal
                    if uploaded_file:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        img = Image.open(uploaded_file)
                        response = model.generate_content([user_prompt, img])
                    else:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(user_prompt)

                    st.markdown(response.text)
                    
                    # Save to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.text
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
