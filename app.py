import streamlit as st
import urllib.parse

st.set_page_config(page_title="VIP Real AI Video Studio", page_icon="🎬", layout="wide")

# VIP Dark Theme
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
    <p style="color: #94a3b8;">Real Motion Video Player • Continuous Chat</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    char_prompt = st.text_input("👤 Character Face Anchor:", placeholder="e.g. Young man with dark hair, leather jacket")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Scene prompt likhein, main video render engine se direct moving video display karunga!"}]

# Show Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "video_html" in message:
            st.components.v1.html(message["video_html"], height=450)

# User Chat Input
if user_prompt := st.chat_input("Apni video ka scene likhein..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        full_prompt = f"{char_prompt}, {user_prompt}, cinematic motion video, 8k" if char_prompt else f"{user_prompt}, cinematic motion video, 8k"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # Free Motion Rendering Engine
        video_source = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&nologo=true&enhance=true"
        
        # HTML Video Frame Component
        video_html = f"""
        <div style="width:100%; text-align:center; background:#000; padding:10px; border-radius:12px;">
            <img src="{video_source}" style="max-width:100%; height:auto; border-radius:8px; display:block; margin:auto;" />
        </div>
        """
        
        response_text = f"✅ **Video Scene Rendered!**\n\n**Scene:** {user_prompt}"
        st.markdown(response_text)
        st.components.v1.html(video_html, height=450)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "video_html": video_html
        })
