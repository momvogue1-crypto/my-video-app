import streamlit as st
import requests
import base64
import random
import io

# ============================================================
# MISWAR'S CREATORS — AI IMAGE STUDIO
# Pollinations Image-to-Image + High Resolution
# ============================================================

st.set_page_config(
    page_title="Miswar's Creators",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #f7f7f8;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
    color: #111111;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 17px;
    margin-bottom: 30px;
}

div.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 700;
    min-height: 48px;
}

.reference-box {
    padding: 15px;
    border-radius: 15px;
    background: white;
    border: 1px solid #dddddd;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎨 MISWAR\'S CREATORS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI Image Studio • Reference Image • High Resolution</div>',
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content":
            "👋 Welcome to **Miswar's Creators**!\n\n"
            "Upload reference images, write your prompt, choose a model and generate."
        }
    ]

# ============================================================
# IMAGE SIZE
# ============================================================

size_mapping = {
    "16:9 — YouTube Thumbnail": (1920, 1080),
    "9:16 — Shorts / Reels": (1080, 1920),
    "1:1 — Square": (1536, 1536),
    "4:5 — Instagram": (1080, 1350),
    "3:4 — Vertical": (1080, 1440),
    "4:5 — High Quality": (1536, 1920),
}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Studio Controls")

    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    st.subheader("🔑 Pollinations API")

    api_key = st.text_input(
        "Pollinations API Key",
        type="password",
        help="Use your Pollinations API key. Keep secret keys server-side."
    )

    st.caption(
        "Your key is used only for the current Streamlit session."
    )

    st.divider()

    # --------------------------------------------------------
    # REFERENCE IMAGES
    # --------------------------------------------------------

    st.subheader("🖼️ Reference Images")

    uploaded_files = st.file_uploader(
        "Upload reference images",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Upload up to 6 images."
    )

    if uploaded_files and len(uploaded_files) > 6:
        st.warning("Maximum 6 images allowed.")
        uploaded_files = uploaded_files[:6]

    if uploaded_files:

        st.success(
            f"✅ {len(uploaded_files)} reference image(s) attached"
        )

        cols = st.columns(2)

        for idx, file in enumerate(uploaded_files):

            with cols[idx % 2]:

                st.image(
                    file,
                    caption=f"Reference {idx + 1}",
                    use_container_width=True
                )

    st.divider()

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    st.subheader("🧠 Image Model")

    model = st.selectbox(
        "Choose Model",
        [
            "nanobanana-2",
            "nanobanana-pro",
            "seedream5",
            "gptimage-large",
            "kontext",
            "flux"
        ],
        index=0
    )

    st.caption(
        "For reference-based generation, try Nano Banana 2, "
        "Nano Banana Pro, Seedream 5 or Kontext first."
    )

    st.divider()

    # --------------------------------------------------------
    # ASPECT RATIO
    # --------------------------------------------------------

    st.subheader("📐 Image Size")

    aspect_ratio_label = st.selectbox(
        "Aspect Ratio",
        list(size_mapping.keys())
    )

    width, height = size_mapping[aspect_ratio_label]

    st.caption(
        f"Output: **{width} × {height} px**"
    )

    st.divider()

    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    st.subheader("✨ Quality")

    quality = st.selectbox(
        "Generation Quality",
        [
            "high",
            "medium",
            "low"
        ],
        index=0
    )

    # --------------------------------------------------------
    # SEED
    # --------------------------------------------------------

    use_random_seed = st.checkbox(
        "🎲 Random Seed",
        value=True
    )

    if use_random_seed:
        seed = random.randint(1, 999999999)
    else:
        seed = st.number_input(
            "Seed",
            min_value=1,
            max_value=999999999,
            value=123456
        )

    st.divider()

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        type="secondary",
        use_container_width=True
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content":
                "👋 Chat cleared. Upload a reference and create something new!"
            }
        ]

        st.rerun()


# ============================================================
# HELPER: FILE → DATA URL
# ============================================================

def file_to_data_url(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    mime_type = uploaded_file.type or "image/png"

    encoded = base64.b64encode(file_bytes).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


# ============================================================
# HELPER: GENERATE IMAGE
# ============================================================

def generate_image(
    prompt,
    api_key,
    model,
    width,
    height,
    quality,
    seed,
    uploaded_files
):

    endpoint = "https://gen.pollinations.ai/v1/images/edits"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # --------------------------------------------------------
    # IMPORTANT:
    # Multipart request sends the actual uploaded image.
    # This is what your previous code was missing.
    # --------------------------------------------------------

    files = []

    if uploaded_files:

        for uploaded_file in uploaded_files:

            files.append(
                (
                    "image",
                    (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "image/png"
                    )
                )
            )

    # --------------------------------------------------------
    # STRONG REFERENCE INSTRUCTIONS
    # --------------------------------------------------------

    if uploaded_files:

        reference_instruction = """
REFERENCE IMAGE INSTRUCTIONS:

The uploaded image(s) are the primary visual reference.

Carefully analyze the reference image(s) before generating.

Preserve the important visual identity and design information from
the reference image(s), especially:

- clothing / dress design
- garment structure
- sleeve design
- neckline
- fabric appearance
- color
- color placement
- patterns
- embroidery
- accessories
- overall styling
- proportions
- pose when requested
- important visual details

Do NOT ignore the reference image.

Do NOT replace the reference design with an unrelated design.

If the user's prompt asks for a modification, modify the reference
while keeping the requested reference characteristics recognizable.

The final image must visibly correspond to the uploaded reference.
"""

        final_prompt = f"""
{reference_instruction}

USER REQUEST:
{prompt}

OUTPUT QUALITY:
Professional commercial fashion photography,
photorealistic,
extremely detailed,
sharp fabric texture,
accurate garment construction,
realistic skin,
realistic lighting,
high dynamic range,
professional photography,
clean composition,
premium editorial quality.

IMPORTANT:
Follow the user's request first.
Use the uploaded reference image as the visual source.
Do not create a random unrelated image.
"""

    else:

        final_prompt = f"""
USER REQUEST:
{prompt}

Create a professional photorealistic image.

Extremely detailed,
sharp textures,
realistic lighting,
professional commercial photography,
premium editorial quality,
clean composition,
high dynamic range.
"""

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    data = {
        "model": model,
        "prompt": final_prompt,
        "width": str(width),
        "height": str(height),
        "quality": quality,
        "seed": str(seed)
    }

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    response = requests.post(
        endpoint,
        headers=headers,
        data=data,
        files=files if files else None,
        timeout=300
    )

    # --------------------------------------------------------
    # ERROR HANDLING
    # --------------------------------------------------------

    if response.status_code != 200:

        try:
            error_data = response.json()
        except Exception:
            error_data = response.text

        raise RuntimeError(
            f"Pollinations API Error {response.status_code}: "
            f"{error_data}"
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    content_type = response.headers.get(
        "content-type",
        ""
    ).lower()

    if "image" in content_type:

        return response.content

    # Some API responses may return JSON.
    try:

        result = response.json()

        # Common possibilities
        if "data" in result:

            first = result["data"][0]

            if "b64_json" in first:

                return base64.b64decode(
                    first["b64_json"]
                )

            if "url" in first:

                image_response = requests.get(
                    first["url"],
                    timeout=300
                )

                image_response.raise_for_status()

                return image_response.content

        raise RuntimeError(
            f"Unexpected Pollinations response: {result}"
        )

    except ValueError:

        raise RuntimeError(
            "Pollinations returned an unexpected response."
        )


# ============================================================
# DISPLAY OLD MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("image_bytes"):

            st.image(
                message["image_bytes"],
                use_container_width=True
            )


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = st.chat_input(
    "Describe the image you want to create..."
)


# ============================================================
# GENERATION
# ============================================================

if user_prompt:

    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not api_key:

        st.error(
            "⚠️ Please enter your Pollinations API key in the sidebar."
        )

        st.stop()

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        status = st.empty()

        try:

            if uploaded_files:

                status.info(
                    "🖼️ Reading reference image(s) and preparing "
                    "image-to-image generation..."
                )

            else:

                status.info(
                    "🎨 Preparing image generation..."
                )

            with st.spinner(
                "🔥 Miswar's Creators is generating your image..."
            ):

                image_bytes = generate_image(
                    prompt=user_prompt,
                    api_key=api_key,
                    model=model,
                    width=width,
                    height=height,
                    quality=quality,
                    seed=seed,
                    uploaded_files=uploaded_files
                )

            status.empty()

            st.success(
                "✅ Image generated successfully!"
            )

            st.image(
                image_bytes,
                caption=f"{model} • {width}×{height}",
                use_container_width=True
            )

            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            st.download_button(
                label="⬇️ Download HD Image",
                data=image_bytes,
                file_name="miswars_creators_image.png",
                mime="image/png",
                use_container_width=True
            )

            # ------------------------------------------------
            # INFO
            # ------------------------------------------------

            info_text = (
                f"✨ **Generated Successfully**\n\n"
                f"**Model:** `{model}`  \n"
                f"**Size:** `{width} × {height}`  \n"
                f"**Quality:** `{quality}`  \n"
                f"**Seed:** `{seed}`"
            )

            if uploaded_files:

                info_text += (
                    f"  \n"
                    f"**References:** `{len(uploaded_files)}`"
                )

            st.markdown(info_text)

            # ------------------------------------------------
            # SAVE CHAT
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": info_text,
                    "image_bytes": image_bytes
                }
            )

        except Exception as e:

            status.empty()

            st.error(
                "❌ Image generation failed."
            )

            st.code(
                str(e)
            )

            st.info(
                "Check your Pollinations API key, selected model, "
                "image format and API availability."
            )
