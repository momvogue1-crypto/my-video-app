import streamlit as st
from google import genai
from PIL import Image

# 1. Page Configuration & Theme
st.set_page_config(
    page_title="Miswar's Creators AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; }
    p, span, label, h1, h2, h3, h4, h5, h6 { color: #111111 !important; }
    section[data-testid="stSidebar"] { background-color: #f7f7f8 !important; border-right: 1px solid #e5e5e5; }
    .main-title { font-size: 2.5rem; font-weight: 800; text-align: center; color: #000000 !important; margin-bottom: 20px; }
    div[data-testid="stChatInput"] { border-radius: 20px; border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-title">Miswar\'s Creators AI 🤖</div>', unsafe_allow_html=True)

# 2. Sidebar Controls
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("🔑 Enter Gemini API Key:", type="password")
    
    st.divider()
    st.subheader("🖼️ Upload Image (Optional)")
    uploaded_file = st.file_uploader("Image ke bare mein poochne ke liye:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Attached Image", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. Chat Session Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **Miswar's Creators**! Main Google Gemini AI se powered hoon. Kuch bhi pochhein!"}
    ]

# Display Existing Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. User Interaction & Response Logic
if user_prompt := st.chat_input("Ask Gemini anything..."):
    if not api_key:
        st.error("⚠️ Pehle Sidebar mein apni Gemini API Key enter karein!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Miswar's AI is thinking..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # Using gemini-1.5-flash for free tier stability
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[user_prompt, img]
                        )
                    else:
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=user_prompt
                        )

                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})

                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        st.error("⏳ Google API Limit Hit ho gayi hai! 30-40 seconds ruk kar dobara try karein ya Google AI Studio se NAYI API KEY banayein.")
                    else:
                        st.error(f"Error: {err_msg}")
