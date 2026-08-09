import streamlit as st
import requests
import time

# Page Config
st.set_page_config(page_title="VIP Real AI Video Studio", page_icon="🎬", layout="wide")

# Dark Theme Style
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    .vip-header { text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.05); border-radius: 16px; margin-bottom: 25px; }
    .vip-title { font-size: 2.5rem; font-weight: 800; background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="vip-header">
    <div class="vip-title">✨ Gemini VIP AI Video Studio</div>
    <p style="color: #94a3b8;">Real MP4 Video Generator • Chat Interface</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Character Anchor")
    char_prompt = st.text_input("👤 Character Face Anchor:", placeholder="e.g. Young man with dark hair, leather jacket")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize Memory
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Scene prompt likhein, main real video render kar dunga!"}]

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "video_url" in message:
            st.video(message["video_url"])

# Input
if user_prompt := st.chat_input("Apni video ka scene likhein..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("🎬 Real MP4 Video Render Ho Rahi Hai (15-30 Sec Wait Karein)..."):
            full_prompt = f"{char_prompt}, {user_prompt}, 8k resolution, highly detailed" if char_prompt else f"{user_prompt}, 8k resolution"
            
            # HuggingFace Free Video Engine API
            API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"
            
            payload = {"inputs": full_prompt}
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                video_bytes = response.content
                st.success("✅ Real Video Ready!")
                st.video(video_bytes)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ **Video Rendered!**\n**Scene:** {user_prompt}",
                    "video_url": video_bytes
                })
            else:
                # Fallback MP4 Video Engine
                fallback_video = f"https://image.pollinations.ai/prompt/{full_prompt.replace(' ', '%20')}?width=1280&height=720&model=flux"
                st.warning("Server busy tha, High Quality Render Frame dikhaya ja raha hai:")
                st.image(fallback_video, use_container_width=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ **Frame Ready!**\n**Scene:** {user_prompt}"
                })
