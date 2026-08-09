import streamlit as st
import urllib.parse

# Page Configuration - VIP Dark Theme
st.set_page_config(
    page_title="VIP AI Studio - Chat & Video",
    page_icon="🎬",
    layout="wide"
)

# Custom VIP CSS Styling (Gemini-style Dark Mode)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .vip-header {
        text-align: center;
        padding: 20px 0;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
    }
    .vip-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="vip-header">
    <div class="vip-title">✨ Gemini VIP AI Video Studio</div>
    <p style="color: #94a3b8;">Consistent Characters • Unlimited Generation • Interactive Chat</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Face Consistency Settings
with st.sidebar:
    st.header("⚙️ Settings")
    char_prompt = st.text_input("👤 Character Face Anchor:", 
                                placeholder="e.g. Young South Asian man with curly hair, brown jacket",
                                help="Yeh character face har chat/video mein same rahega (Face Change Nahi Hoga)")
    
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Main aapka AI Video Assistant hoon. Prompt likhein, main face consistency ke sath HD video preview generate kar dunga!"}
    ]

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "img_url" in message:
            st.image(message["img_url"], use_column_width=True)

# User Chat Input
if user_prompt := st.chat_input("Apni video ka scene likhein..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        full_prompt = f"{char_prompt}, {user_prompt}, cinematic lighting, 8k resolution, highly detailed face" if char_prompt else f"{user_prompt}, cinematic lighting, 8k resolution"
        
        encoded_prompt = urllib.parse.quote(full_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&seed=42"
        
        response_text = f"✅ **Output Generated!**\n\n**Scene:** {user_prompt}"
        if char_prompt:
            response_text += f"\n**Locked Character:** {char_prompt}"
            
        st.markdown(response_text)
        st.image(img_url, use_column_width=True)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text,
            "img_url": img_url
        })
