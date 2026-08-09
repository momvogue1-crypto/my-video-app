import streamlit as st
import urllib.parse
import random

st.set_page_config(
    page_title="Miswar's Creators",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; }
    p, span, label, h1, h2, h3, h4, h5, h6 { color: #111111 !important; }
    section[data-testid="stSidebar"] { background-color: #f7f7f8 !important; border-right: 1px solid #e5e5e5; }
    .chatgpt-header { text-align: center; padding: 10px 0 20px 0; margin-bottom: 10px; border-bottom: 1px solid #eaeaea; }
    .main-title { font-size: 2.8rem; font-weight: 800; color: #000000 !important; letter-spacing: -0.5px; }
    div[data-testid="stChatInput"] { border-radius: 20px; border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="chatgpt-header">
    <div class="main-title">Miswar's Creators</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Studio Controls")
    
    aspect_ratio_label = st.selectbox(
        "📐 Image Size Ratio",
        ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)", "4:5 (Instagram)", "3:4 (Vertical)"]
    )
    
    size_mapping = {
        "16:9 (Landscape)": (1920, 1080),
        "9:16 (Portrait)": (1080, 1920),
        "1:1 (Square)": (1080, 1080),
        "4:5 (Instagram)": (1080, 1350),
        "3:4 (Vertical)": (1080, 1440)
    }
    
    width, height = size_mapping[aspect_ratio_label]
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Apna detailed text prompt likhein, main Ultra HD image generate kar doonga."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "img_url" in message:
            st.image(message["img_url"], use_container_width=True)

if user_prompt := st.chat_input("Describe the image you want to create..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Miswar's Creators Engine is generating your Ultra HD image..."):
            
            # Enhancing prompt with high quality tags
            enhanced_prompt = f"{user_prompt}, 8k resolution, highly detailed, photorealistic, masterpiece"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Generate unique seed every time for fresh results
            seed = random.randint(1, 999999)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&model=flux"
            
            response_text = f"✨ **Here is your Ultra HD Image!**\n\n**Ratio:** `{aspect_ratio_label}`"
            
            st.markdown(response_text)
            st.image(image_url, use_container_width=True)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "img_url": image_url
            })
