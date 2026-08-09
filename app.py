import streamlit as st
import urllib.parse
import requests

# Page Configuration - Miswar's Creators VIP Theme
st.set_page_config(
    page_title="Miswar's Creators - AI Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling to mimic ChatGPT Dark Mode with VIP Classy Aesthetics
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #212121;
        color: #ececec;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header Area */
    .chatgpt-header {
        text-align: center;
        padding: 15px 0 5px 0;
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    .owner-tag {
        font-family: 'Georgia', serif;
        font-style: italic;
        color: #9b9b9b;
        font-size: 1.2rem;
        margin-top: -5px;
    }
    .owner-name {
        font-weight: bold;
        color: #e2e8f0;
        letter-spacing: 0.5px;
    }
    
    /* Input Box styling like ChatGPT */
    div[data-testid="stChatInput"] {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Main Header - Branding & Signature
st.markdown("""
<div class="chatgpt-header">
    <div class="main-title">Miswar's Creators</div>
    <div class="owner-tag">Designed by <span class="owner-name">Miswar Ilyas</span> (Classy Owner)</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Options
with st.sidebar:
    st.title("⚙️ Studio Controls")
    
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
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Main aapka AI Image Creator hoon. ChatGPT ki tarah apna koi bhi idea likhein, main Ultra HD image generate kar dunga!"}
    ]

# Display Existing Chat Messages (ChatGPT Style)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "img_url" in message:
            st.image(message["img_url"], use_container_width=True)

# ChatGPT-style Chat Input Bar at Bottom
if user_prompt := st.chat_input("Ask Miswar's Creators to create an image..."):
    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate Image Response
    with st.chat_message("assistant"):
        with st.spinner("Miswar's Creators Engine is generating your Ultra HD image..."):
            encoded_prompt = urllib.parse.quote(user_prompt)
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
