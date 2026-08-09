import streamlit as st
import fal_client
import os

st.set_page_config(page_title="VIP AI Video Studio", page_icon="🎬", layout="wide")

st.title("🎬 Real AI Video Generator (MP4)")

api_key = st.text_input("Enter Fal.ai API Key:", type="password")
prompt = st.text_area("Video Scene Prompt:")

if st.button("🚀 Generate Real MP4 Video"):
    if not api_key or not prompt:
        st.warning("API Key aur Prompt dono daalein!")
    else:
        try:
            os.environ["FAL_KEY"] = api_key
            
            with st.spinner("Real MP4 Video Render ho rahi hai (1-2 min wait karein)..."):
                handler = fal_client.submit(
                    "fal-ai/ltx-video",
                    arguments={"prompt": prompt}
                )
                result = handler.get()
                video_url = result['video']['url']
                
                st.success("✅ Real Moving Video Ready!")
                st.video(video_url)
        except Exception as e:
            st.error(f"Error: {str(e)}")
