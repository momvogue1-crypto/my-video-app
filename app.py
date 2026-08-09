import streamlit as st
import urllib.parse
import random

# Page Configuration - Miswar's Creators VIP Clean Theme
st.set_page_config(
    page_title="Miswar's Creators",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Clean White & Black Contrast
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f7f7f8 !important;
        border-right: 1px solid #e5e5e5;
    }
    .chatgpt-header {
        text-align: center;
        padding: 10px 0 20px 0;
        margin-bottom: 10px;
        border-bottom: 1px solid #eaeaea;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #000000 !important;
        letter-spacing: -0.5px;
    }
    div[data-testid="stChatInput"] {
        border-radius: 20px;
        border: 1px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div class="chatgpt-header">
    <div class="main-title">Miswar's Creators</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Options
with st.sidebar:
    st.title("⚙️ Studio Controls")
    
    # Image Upload Section (Up to 6 Images)
    st.subheader("🖼️ Reference Images (Up to 6)")
    uploaded_files = st.file_uploader(
        "Upload reference images:", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 6:
            st.error("⚠️ Max 6 images allowed!")
            uploaded_files = uploaded_files[:6]
        
        st.success(f"✅ {len(uploaded_files)} Images Attached!")
        
        cols = st.columns(3)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(file, use_container_width=True)
    
    st.divider()
    
    # Aspect Ratio Functionality
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

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Write your detailed prompt or attach reference images in the sidebar to generate Ultra-HD art."}
    ]

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "img_url" in message:
            st.image(message["img_url"], use_container_width=True)

# User Chat Input
if user_prompt := st.chat_input("Ask Miswar's Creators to generate an image..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Miswar's Creators Engine rendering 8K Ultra-HD Image..."):
            
            # Enhancing prompt quality
            base_prompt = user_prompt
            if uploaded_files:
                base_prompt = f"Inspired by uploaded reference images, {user_prompt}"
            
            enhanced_prompt = f"{base_prompt}, photorealistic, 8k resolution, Unreal Engine 5 render, cinematic lighting, masterpiece, hyperdetailed"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Flux Engine Render
            seed = random.randint(1000, 99999)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&model=flux&enhance=true"
            
            response_text = f"✨ **Here is your Ultra HD Image!**\n\n**Ratio:** `{aspect_ratio_label}`"
            if uploaded_files:
                response_text += f"\n**References Attached:** `{len(uploaded_files)} Images`"
            
            st.markdown(response_text)
            st.image(image_url, use_container_width=True)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "img_url": image_url
            })
