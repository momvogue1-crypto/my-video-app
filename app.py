import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image, ImageOps
from io import BytesIO
import random
import tempfile
import os


# ============================================================
# MISWAR'S CREATORS
# FREE REFERENCE IMAGE AI EDITOR
# Powered by public Hugging Face Qwen Image Edit Space
# ============================================================

st.set_page_config(
    page_title="Miswar's Creators",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #f7f7f8;
}

.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    color: #111111;
    margin-top: 10px;
    margin-bottom: 0px;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 16px;
    margin-bottom: 30px;
}

.section-title {
    font-size: 20px;
    font-weight: 800;
}

div.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    font-weight: 800;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 800;
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
    'FREE AI IMAGE STUDIO • REFERENCE IMAGE EDITING • '
    'QWEN IMAGE EDIT'
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
            "👋 **Welcome to Miswar's Creators!**\n\n"
            "Upload a reference image, write your instruction, "
            "and generate your edited image."
        }
    ]


# ============================================================
# HUGGING FACE SPACE
# ============================================================

SPACE_ID = "Qwen/Qwen-Image-Edit"


# ============================================================
# CONNECT TO FREE QWEN SPACE
# ============================================================

@st.cache_resource(show_spinner=False)
def get_qwen_client():

    return Client(
        SPACE_ID,
        verbose=False
    )


# ============================================================
# ASPECT RATIO
# ============================================================

RATIO_MAP = {

    "16:9": (16, 9),

    "9:16": (9, 16),

    "1:1": (1, 1),

    "4:5": (4, 5),

    "3:4": (3, 4),

    "4:3": (4, 3),

    "3:2": (3, 2),

    "2:3": (2, 3)
}


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_reference_image(
    uploaded_file,
    ratio
):

    image = Image.open(
        uploaded_file
    ).convert("RGB")

    target_w, target_h = RATIO_MAP[
        ratio
    ]

    original_w, original_h = image.size

    original_ratio = (
        original_w / original_h
    )

    target_ratio = (
        target_w / target_h
    )

    # --------------------------------------------------------
    # We avoid aggressive cropping.
    # Instead we fit the image inside target ratio.
    # --------------------------------------------------------

    if original_ratio > target_ratio:

        # Image is wider.
        new_h = original_h

        new_w = int(
            original_h * target_ratio
        )

        left = (
            original_w - new_w
        ) // 2

        image = image.crop(
            (
                left,
                0,
                left + new_w,
                original_h
            )
        )

    else:

        # Image is taller.
        new_w = original_w

        new_h = int(
            original_w / target_ratio
        )

        top = (
            original_h - new_h
        ) // 2

        image = image.crop(
            (
                0,
                top,
                original_w,
                top + new_h
            )
        )

    # --------------------------------------------------------
    # Resize to a reasonable generation size
    # --------------------------------------------------------

    base = 1024

    if target_w >= target_h:

        final_w = base

        final_h = int(
            base / target_ratio
        )

    else:

        final_h = base

        final_w = int(
            base * target_ratio
        )

    image = image.resize(
        (
            final_w,
            final_h
        ),
        Image.Resampling.LANCZOS
    )

    return image


# ============================================================
# SAVE TEMP IMAGE
# ============================================================

def save_temp_image(image):

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    )

    image.save(
        temp_file.name,
        format="PNG"
    )

    temp_file.close()

    return temp_file.name


# ============================================================
# BUILD STRONG PROMPT
# ============================================================

def build_prompt(
    user_prompt,
    ratio,
    quality,
    keep_reference
):

    reference_instruction = ""

    if keep_reference:

        reference_instruction = """
VERY IMPORTANT REFERENCE IMAGE INSTRUCTIONS:

Use the uploaded image as the PRIMARY visual reference.

Preserve the important visual identity of the reference.

Pay special attention to:

- clothing design
- dress structure
- garment silhouette
- exact dress color
- color placement
- fabric appearance
- neckline
- sleeves
- embroidery
- prints
- patterns
- accessories
- overall styling
- important visual details

DO NOT ignore the reference image.

DO NOT create a completely unrelated dress.

If the user asks to change the model, background,
pose, camera position, lighting or environment,
make those changes while keeping the important
reference clothing/design recognizable.

If the user says KEEP THE DRESS COLOR,
do not change the dress color.

If the reference shows a complete outfit,
preserve the outfit design accurately.
"""

    final_prompt = f"""
{reference_instruction}

USER REQUEST:

{user_prompt}

COMPOSITION:

Create the final image in {ratio} aspect ratio.

QUALITY:

{quality}

Create a premium, highly detailed,
photorealistic commercial image.

Realistic human anatomy,
realistic skin,
realistic hair,
realistic fabric texture,
accurate garment construction,
sharp clothing details,
natural lighting,
professional shadows,
high dynamic range,
premium fashion photography,
professional editorial photography,
clean composition.

Make the final image visually polished
and professionally photographed.

Do not add unnecessary objects.

Do not change important reference details
unless specifically requested by the user.
"""

    return final_prompt


# ============================================================
# GENERATE USING QWEN SPACE
# ============================================================

def generate_with_qwen(
    image_path,
    prompt
):

    client = get_qwen_client()

    seed = random.randint(
        0,
        2147483647
    )

    # --------------------------------------------------------
    # Qwen public Space function
    # --------------------------------------------------------

    result = client.predict(

        handle_file(image_path),

        prompt,

        seed,

        True,

        4.0,

        50,

        True,

        api_name="/infer"
    )

    # --------------------------------------------------------
    # Result normally contains:
    # [generated_image, seed]
    # --------------------------------------------------------

    if isinstance(
        result,
        (list, tuple)
    ):

        generated = result[0]

    else:

        generated = result

    # --------------------------------------------------------
    # Handle file path
    # --------------------------------------------------------

    if isinstance(
        generated,
        str
    ):

        if os.path.exists(
            generated
        ):

            image = Image.open(
                generated
            ).convert("RGB")

            return image

        # Sometimes Gradio returns a URL.
        if generated.startswith(
            "http"
        ):

            import requests

            response = requests.get(
                generated,
                timeout=120
            )

            response.raise_for_status()

            return Image.open(
                BytesIO(
                    response.content
                )
            ).convert("RGB")

    # --------------------------------------------------------
    # PIL image
    # --------------------------------------------------------

    if isinstance(
        generated,
        Image.Image
    ):

        return generated.convert(
            "RGB"
        )

    raise RuntimeError(
        "Qwen returned an unsupported image format."
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Studio Controls")

    # --------------------------------------------------------
    # ENGINE STATUS
    # --------------------------------------------------------

    st.subheader("🧠 AI Engine")

    st.success(
        "🟢 Qwen Image Edit"
    )

    st.caption(
        "Free public Hugging Face ZeroGPU Space"
    )

    st.divider()

    # --------------------------------------------------------
    # REFERENCE IMAGE
    # --------------------------------------------------------

    st.subheader("🖼️ Reference Image")

    uploaded_files = st.file_uploader(
        "Upload your reference image",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:

        # ----------------------------------------------------
        # Qwen Space accepts one primary image.
        # ----------------------------------------------------

        if len(uploaded_files) > 1:

            st.info(
                "For the strongest reference accuracy, "
                "use ONE primary reference image."
            )

        st.success(
            f"✅ {len(uploaded_files)} image(s) uploaded"
        )

        for i, file in enumerate(
            uploaded_files
        ):

            st.image(
                file,
                caption=f"Reference {i + 1}",
                use_container_width=True
            )

    st.divider()

    # --------------------------------------------------------
    # ASPECT RATIO
    # --------------------------------------------------------

    st.subheader("📐 Aspect Ratio")

    aspect_ratio = st.selectbox(
        "Image Ratio",
        list(
            RATIO_MAP.keys()
        ),
        index=0
    )

    st.caption(
        f"Selected: **{aspect_ratio}**"
    )

    st.divider()

    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    st.subheader("✨ Quality")

    quality = st.selectbox(
        "Rendering Quality",
        [
            "Ultra realistic fashion photography",
            "Premium commercial photography",
            "Luxury editorial photography",
            "Cinematic photorealism",
            "Natural realistic photography"
        ],
        index=0
    )

    st.divider()

    # --------------------------------------------------------
    # REFERENCE STRENGTH
    # --------------------------------------------------------

    st.subheader("🎯 Reference Priority")

    keep_reference = st.checkbox(
        "Preserve reference design",
        value=True
    )

    if keep_reference:

        st.caption(
            "The AI will strongly prioritize "
            "the uploaded reference."
        )

    else:

        st.caption(
            "The AI has more freedom to redesign."
        )

    st.divider()

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get(
            "image"
        ) is not None:

            st.image(
                message["image"],
                use_container_width=True
            )


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = st.chat_input(
    "✨ Describe exactly what you want..."
)


# ============================================================
# GENERATION
# ============================================================

if user_prompt:

    # --------------------------------------------------------
    # REQUIRE REFERENCE
    # --------------------------------------------------------

    if not uploaded_files:

        st.error(
            "🖼️ Please upload at least ONE reference image."
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
                "🔥 Connecting to free Qwen GPU..."
            ):

                # ------------------------------------------------
                # Use FIRST image as primary reference.
                # ------------------------------------------------

                primary_file = (
                    uploaded_files[0]
                )

                # ------------------------------------------------
                # Prepare image
                # ------------------------------------------------

                reference_image = (
                    prepare_reference_image(
                        primary_file,
                        aspect_ratio
                    )
                )

                # ------------------------------------------------
                # Save temporary file
                # ------------------------------------------------

                image_path = (
                    save_temp_image(
                        reference_image
                    )
                )

                # ------------------------------------------------
                # Build prompt
                # ------------------------------------------------

                final_prompt = build_prompt(

                    user_prompt,

                    aspect_ratio,

                    quality,

                    keep_reference
                )

            # ----------------------------------------------------
            # GENERATE
            # ----------------------------------------------------

            with st.spinner(
                "🎨 Qwen is studying the reference "
                "and generating your image..."
            ):

                result_image = (
                    generate_with_qwen(
                        image_path,
                        final_prompt
                    )
                )

            # ----------------------------------------------------
            # CLEAN TEMP FILE
            # ----------------------------------------------------

            try:

                os.remove(
                    image_path
                )

            except Exception:

                pass

            # ----------------------------------------------------
            # DISPLAY
            # ----------------------------------------------------

            st.success(
                "✅ Image generated successfully!"
            )

            st.image(
                result_image,
                caption=(
                    f"Qwen Image Edit • "
                    f"{aspect_ratio}"
                ),
                use_container_width=True
            )

            # ----------------------------------------------------
            # PNG DOWNLOAD
            # ----------------------------------------------------

            output = BytesIO()

            result_image.save(
                output,
                format="PNG"
            )

            image_bytes = (
                output.getvalue()
            )

            st.download_button(

                "⬇️ Download HD Image",

                data=image_bytes,

                file_name=
                    "miswars_creators_qwen.png",

                mime="image/png",

                use_container_width=True
            )

            # ----------------------------------------------------
            # INFO
            # ----------------------------------------------------

            info = (
                "✨ **Image Generated Successfully**\n\n"
                f"**Engine:** `Qwen Image Edit`  \n"
                f"**Aspect Ratio:** `{aspect_ratio}`  \n"
                f"**Reference:** `Primary reference preserved`  \n"
                f"**Quality:** `{quality}`"
            )

            st.markdown(
                info
            )

            # ----------------------------------------------------
            # SAVE HISTORY
            # ----------------------------------------------------

            st.session_state.messages.append(
                {
                    "role":
                        "assistant",

                    "content":
                        info,

                    "image":
                        result_image
                }
            )

        except Exception as e:

            st.error(
                "❌ Generation failed."
            )

            st.code(
                str(e)
            )

            st.warning(
                """
If the error says the Space is busy, queued,
GPU unavailable, or quota exceeded, wait a little
and try again.

This version uses a public free ZeroGPU Space,
so its free GPU capacity is shared with other users.
"""
            )
