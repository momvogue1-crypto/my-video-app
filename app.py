import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import random


# ============================================================
# MISWAR'S CREATORS
# Gemini Image Generation + Reference Images
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
    color: #111111;
    margin-bottom: 5px;
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
    min-height: 48px;
    font-weight: 700;
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
    '<div class="subtitle">'
    'Gemini AI Image Studio • Reference Images • HD Generation'
    '</div>',
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
            "Upload your reference image and describe "
            "exactly what you want."
        }
    ]


# ============================================================
# GEMINI API KEY
# ============================================================

try:

    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

except Exception:

    GEMINI_API_KEY = ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Studio Controls")

    # --------------------------------------------------------
    # API STATUS
    # --------------------------------------------------------

    st.subheader("🔑 Gemini API")

    if GEMINI_API_KEY:

        st.success("🟢 Gemini API Connected")

    else:

        st.error(
            "Gemini API key not found."
        )

        st.caption(
            "Add GEMINI_API_KEY to "
            ".streamlit/secrets.toml"
        )

    st.divider()

    # --------------------------------------------------------
    # REFERENCE IMAGES
    # --------------------------------------------------------

    st.subheader("🖼️ Reference Images")

    uploaded_files = st.file_uploader(
        "Upload reference images",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        accept_multiple_files=True
    )

    # Gemini 2.5 Flash Image works best with up to 3 images.
    if uploaded_files:

        if len(uploaded_files) > 3:

            st.warning(
                "Gemini 2.5 Flash Image works best "
                "with up to 3 reference images. "
                "Only the first 3 will be used."
            )

            uploaded_files = uploaded_files[:3]

        st.success(
            f"✅ {len(uploaded_files)} reference image(s)"
        )

        cols = st.columns(2)

        for index, file in enumerate(
            uploaded_files
        ):

            with cols[index % 2]:

                st.image(
                    file,
                    caption=f"Reference {index + 1}",
                    use_container_width=True
                )

    st.divider()

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    st.subheader("🧠 Gemini Image Model")

    model = st.selectbox(
        "Choose Model",
        [
            "gemini-2.5-flash-image",
            "gemini-3.1-flash-image"
        ],
        index=0
    )

    if model == "gemini-2.5-flash-image":

        st.caption(
            "Nano Banana — optimized for fast "
            "image generation and editing."
        )

    else:

        st.caption(
            "Nano Banana 2 — higher quality and "
            "up to 4K output, subject to account access."
        )

    st.divider()

    # --------------------------------------------------------
    # ASPECT RATIO
    # --------------------------------------------------------

    st.subheader("📐 Image Size")

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        [
            "16:9",
            "9:16",
            "1:1",
            "4:5",
            "3:4",
            "4:3",
            "3:2",
            "21:9"
        ],
        index=0
    )

    st.caption(
        f"Output ratio: **{aspect_ratio}**"
    )

    st.divider()

    # --------------------------------------------------------
    # RESOLUTION
    # --------------------------------------------------------

    st.subheader("✨ Resolution")

    if model == "gemini-2.5-flash-image":

        resolution = "1K"

        st.info(
            "Gemini 2.5 Flash Image outputs "
            "approximately 1K resolution."
        )

    else:

        resolution = st.selectbox(
            "Output Resolution",
            [
                "1K",
                "2K",
                "4K"
            ],
            index=1
        )

    st.divider()

    # --------------------------------------------------------
    # RANDOM SEED
    # --------------------------------------------------------

    random_seed = random.randint(
        1,
        999999999
    )

    st.caption(
        f"🎲 Generation ID: `{random_seed}`"
    )

    st.divider()

    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    except Exception as e:

        st.error(
            f"Gemini client error: {e}"
        )


# ============================================================
# REFERENCE IMAGE LOADER
# ============================================================

def load_reference_images(files):

    images = []

    for file in files:

        try:

            image = Image.open(
                BytesIO(
                    file.getvalue()
                )
            ).convert("RGB")

            images.append(image)

        except Exception as e:

            st.warning(
                f"Could not read {file.name}: {e}"
            )

    return images


# ============================================================
# GENERATE IMAGE
# ============================================================

def generate_image(
    prompt,
    reference_images,
    model,
    aspect_ratio,
    resolution
):

    # --------------------------------------------------------
    # STRONG REFERENCE INSTRUCTIONS
    # --------------------------------------------------------

    if reference_images:

        reference_prompt = f"""
You are an expert commercial fashion image editor.

The uploaded reference image(s) are IMPORTANT VISUAL
REFERENCES.

Study them carefully before generating the final image.

The user's requested changes should be applied while
preserving the important visual information from the
reference image(s).

REFERENCE PRESERVATION PRIORITIES:

1. Dress / clothing design
2. Exact dress color
3. Color placement
4. Garment silhouette
5. Neckline
6. Sleeves
7. Fabric appearance
8. Embroidery and patterns
9. Accessories
10. Overall styling
11. Important visual details

DO NOT ignore the reference images.

DO NOT invent a completely unrelated dress.

If the user requests a new model, background, pose,
camera angle or composition, change those elements while
keeping the requested reference clothing/design
recognizable.

If the user says to keep the dress color unchanged,
preserve the original color as accurately as possible.

USER REQUEST:

{prompt}

FINAL IMAGE REQUIREMENTS:

Professional commercial fashion photography,
photorealistic,
extremely detailed,
realistic fabric texture,
accurate clothing construction,
natural skin texture,
professional lighting,
realistic shadows,
sharp subject,
clean composition,
premium fashion campaign,
high-end editorial photography.

Create the final image in {aspect_ratio}.
"""

    else:

        reference_prompt = f"""
Create a professional photorealistic image based on
the following request:

{prompt}

Requirements:

Premium commercial photography,
realistic materials,
realistic fabric,
sharp details,
natural skin,
professional lighting,
realistic shadows,
clean composition,
high-end editorial fashion photography,
aspect ratio {aspect_ratio}.
"""

    # --------------------------------------------------------
    # CONTENTS
    # --------------------------------------------------------

    contents = []

    # Put reference images BEFORE the instruction.
    for image in reference_images:

        contents.append(image)

    contents.append(
        reference_prompt
    )

    # --------------------------------------------------------
    # CONFIG
    # --------------------------------------------------------

    image_config = {
        "aspect_ratio": aspect_ratio
    }

    # Gemini 3 image models support image_size.
    if model == "gemini-3.1-flash-image":

        image_config["image_size"] = resolution

    config = types.GenerateContentConfig(

        response_modalities=[
            "IMAGE"
        ],

        response_format={
            "image": image_config
        }
    )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    response = client.models.generate_content(

        model=model,

        contents=contents,

        config=config
    )

    # --------------------------------------------------------
    # FIND IMAGE
    # --------------------------------------------------------

    for part in response.parts:

        if part.inline_data is not None:

            return part.as_image()

    raise RuntimeError(
        "Gemini did not return an image."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get("image"):

            st.image(
                message["image"],
                use_container_width=True
            )


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = st.chat_input(
    "Describe the image you want to create..."
)


# ============================================================
# GENERATE
# ============================================================

if user_prompt:

    # --------------------------------------------------------
    # API CHECK
    # --------------------------------------------------------

    if not GEMINI_API_KEY:

        st.error(
            "❌ Gemini API key is missing."
        )

        st.stop()

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role":
                "user",

            "content":
                user_prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_prompt
        )

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "🔥 Gemini is studying your reference "
                "and generating the image..."
            ):

                reference_images = (
                    load_reference_images(
                        uploaded_files
                        if uploaded_files
                        else []
                    )
                )

                generated_image = generate_image(

                    prompt=user_prompt,

                    reference_images=
                        reference_images,

                    model=model,

                    aspect_ratio=
                        aspect_ratio,

                    resolution=
                        resolution
                )

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            st.success(
                "✅ Image generated successfully!"
            )

            st.image(
                generated_image,
                caption=(
                    f"{model} • "
                    f"{aspect_ratio} • "
                    f"{resolution}"
                ),
                use_container_width=True
            )

            # ------------------------------------------------
            # CONVERT TO PNG
            # ------------------------------------------------

            image_buffer = BytesIO()

            generated_image.save(
                image_buffer,
                format="PNG"
            )

            image_bytes = (
                image_buffer.getvalue()
            )

            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            st.download_button(

                "⬇️ Download HD Image",

                data=image_bytes,

                file_name=
                    "miswars_creators_gemini.png",

                mime="image/png",

                use_container_width=True
            )

            # ------------------------------------------------
            # INFO
            # ------------------------------------------------

            info = (
                f"✨ **Generated Successfully**\n\n"
                f"**Model:** `{model}`  \n"
                f"**Aspect Ratio:** `{aspect_ratio}`  \n"
                f"**Resolution:** `{resolution}`  \n"
                f"**Reference Images:** "
                f"`{len(reference_images)}`"
            )

            st.markdown(info)

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role":
                        "assistant",

                    "content":
                        info,

                    "image":
                        generated_image
                }
            )

        except Exception as e:

            st.error(
                "❌ Gemini image generation failed."
            )

            st.code(
                str(e)
            )

            st.info(
                "If the error mentions quota, billing, "
                "or RESOURCE_EXHAUSTED, your Gemini API "
                "project does not currently have image "
                "generation access."
            )
