import streamlit as st
import urllib.parse
from PIL import Image

# Page Configuration - Miswar's Creators Light Clean Theme
st.set_page_config(
    page_title="Miswar's Creators",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Clean White & Black Contrast
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    /* Global text contrast fix */
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f7f7f8 !important;
        border-right: 1px solid #e5e5e5;
    }
    
    /* Header Area */
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

    /* Input Box styling */
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
    
    # Image Input Option (Image to Image / Image Reference)
    st.subheader("🖼️ Image Input (Optional)")
    uploaded_file = st.file_uploader("Upload reference image:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Reference Image", use_container_width=True)
        st.success("✅ Reference Image Attached!")
    
    st.divider()
    
    # Aspect Ratio Functionality
    aspect_ratio_label = st.selectbox(
        "📐 Image Size Ratio",
        ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)", "4:5 (Instagram)", "3:4 (Vertical)"]
    )
    
    # Map ratios to resolution pixels
    size_mapping = {
        "16:9 (Landscape)": (1920, 1080),
        "9:16 (Portrait)": (1080, 1920),
        "1:1 (Square)": (1080, 1080),
        "4:5 (Instagram)": (1080, 1350),
        "3:4 (Vertical)": (1080, 1440)
    }
    
    width, height = size_mapping[aspect_ratio_label]
    
    st.divider()
    
    # Clear Chat Memory Button
    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Apna scene/prompt likhein ya sidebar se image upload karke modifications bataayein."}
    ]

# Display Existing Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "img_url" in message:
            st.image(message["img_url"], use_container_width=True)

# Chat Input Bar
if user_prompt := st.chat_input("Ask Miswar's Creators to generate or modify an image..."):
    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate Image Response
    with st.chat_message("assistant"):
        with st.spinner("Miswar's Creators Engine is generating your Ultra HD image..."):
            
            # Combine image reference flag in prompt if image uploaded
            final_prompt = user_prompt
            if uploaded_file:
                final_prompt = f"Based on reference style, {user_prompt}"
            
            encoded_prompt = urllib.parse.quote(final_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"
            
            response_text = f"✨ **Here is your Ultra HD Image!**\n\n**Ratio:** `{aspect_ratio_label}`"
            
            st.markdown(response_text)
            st.image(image_url, use_container_width=True)
            
            # Save to conversation history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "img_url": image_url
            })
