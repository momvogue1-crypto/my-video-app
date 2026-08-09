import streamlit as st
import replicate
import os

st.set_page_config(page_title="VIP AI Video Generator", page_icon="🎬", layout="centered")

st.title("🎬 VIP HD AI Video Generator")
st.write("Apna prompt likhein aur high quality HD AI video generate karein!")

api_key = st.text_input("Enter Replicate API Key:", type="password", help="Replicate.com se free API key milti hai")

prompt = st.text_area("Video Prompt:", placeholder="A cinematic shot of a neon cyberpunk city at night, 8k resolution...", height=100)

if st.button("🚀 Generate HD Video", type="primary"):
    if not api_key:
        st.error("Please API key enter karein!")
    elif not prompt:
        st.warning("Please prompt likhein!")
    else:
        try:
            os.environ["REPLICATE_API_TOKEN"] = api_key
            with st.spinner("AI Video Render ho rahi hai, 1-2 minute wait karein..."):
                output = replicate.run(
                    "stability-ai/stable-video-diffusion:3f04d01d45d35424592965b61063f8514d32b6dd1e082ed5fc06e5b6defb1505",
                    input={"prompt": prompt}
                )
                st.success("Video Tayar Hai!")
                st.video(output)
        except Exception as e:
            st.error(f"Error: {str(e)}")
