import streamlit as st
import urllib.parse
import requests

# VIP Page Configuration
st.set_page_config(page_title="VIP AI Studio - Miswar Ilyas", page_icon="🎨", layout="wide")

# Custom Stylish CSS for VIP Look & Classy Headers
st.markdown("""
<style>
    /* Dark Theme Styles */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Elegant Classy VIP Header */
    .vip-header {
        text-align: center;
        padding: 25px 0;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stylish Owner Signature */
    .owner-stylish {
        text-align: center;
        margin-bottom: 30px;
    }
    .stylish-tagline {
        font-family: 'Times New Roman', serif;
        font-style: italic;
        color: #f8fafc;
        font-size: 1.5rem;
    }
    .stylish-owner {
        font-weight: bold;
        font-family: 'Times New Roman', serif;
        color: #e2e8f0;
        font-size: 1.8rem;
        margin-top: 5px;
    }

    /* Input & Control Section Design */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main VIP Classy Header
st.markdown("""
<div class="vip-header">
    <div class="main-title">VIP AI Ultra HD Image Generator</div>
</div>
""", unsafe_allow_html=True)

# Stylish & Classy Owner Signature Section
st.markdown("""
<div class="owner-stylish">
    <div class="stylish-tagline">"Miswar Ilyas"</div>
    <div class="stylish-owner">Classy Owner - The Web</div>
</div>
""", unsafe_allow_html=True)

# Generate Section
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.header("⚙️ Configuration")
    
    # Text input for image description
    prompt_input = st.text_area("Describe your image prompt...", height=150, placeholder="Example: Cinematic portrait of a celestial queen with glowing energy, photorealistic, 8k, extremely detailed")
    
    # Aspect Ratio Selection
    aspect_ratio_label = st.selectbox("Select Size Ratio", ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)", "4:5 (Instagram)", "3:4 (Vertical)"])
    
    # Image Size Mapping (approx. pixels based on ratio)
    size_mapping = {
        "16:9 (Landscape)": (1920, 1080),
        "9:16 (Portrait)": (1080, 1920),
        "1:1 (Square)": (1080, 1080),
        "4:5 (Instagram)": (1080, 1350),
        "3:4 (Vertical)": (1080, 1440)
    }
    
    selected_width, selected_height = size_mapping[aspect_ratio_label]
    
    if st.button("🚀 Generate VIP HD Image"):
        if not prompt_input:
            st.warning("Please enter a prompt first!")
        else:
            with st.spinner("Generating your Ultra HD Image..."):
                # URL Encode prompt & configuration
                encoded_prompt = urllib.parse.quote(prompt_input)
                
                # Free high-speed render engine (Flux-based, high detail)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={selected_width}&height={selected_height}&nologo=true&seed=42"
                
                # Check image existence (simulate success, handles some API cases)
                response = requests.get(image_url)
                if response.status_code == 200:
                    st.session_state.last_generated_image_url = image_url
                    st.success("✅ Ultra HD Image Ready!")
                else:
                    st.error("There was an issue generating the image. Please try again.")

# Output Section
with col2:
    st.header("🖼️ Output")
    
    if 'last_generated_image_url' in st.session_state:
        st.image(st.session_state.last_generated_image_url, use_container_width=True)
