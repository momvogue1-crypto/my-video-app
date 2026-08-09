import streamlit as st
import urllib.parse

# Page Configuration - Miswar's Creators Light Theme
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
    
    # Multiple Image Upload Option (Up to 6 Images)
    st.subheader("🖼️ Reference Images (Up to 6)")
    uploaded_files = st.file_uploader(
        "Upload reference images:", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > 6:
            st.error("⚠️ Aap ziada se ziada 6 images upload kar sakte hain!")
            uploaded_files = uploaded_files[:6]  # Limit to first 6 files
        
        st.success(f"✅ {len(uploaded_files)} Images Attached!")
        
        # Display uploaded images in a small grid
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
    
    # Map ratios to resolution pixels
    size_mapping = {
        "16:9 (Landscape)": (1920, 1080),
        "9:16 (Portrait)": (1080, 1920),
        "1:1 (Square)": (1080
