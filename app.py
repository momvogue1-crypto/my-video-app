import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image
from io import BytesIO
import tempfile
import os
import random
import time


# ============================================================
# MISWAR'S CREATORS AI
# ============================================================

st.set_page_config(
    page_title="Miswar's Creators AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# OFFICIAL QWEN SPACES
# ============================================================

CHAT_SPACE = "Qwen/Qwen3-VL-235B-A22B-Instruct-Demo"
IMAGE_SPACE = "Qwen/Qwen-Image-Edit"


# ============================================================
# PAGE STYLE
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #f7f7f8;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    color: #111111;
    margin-top: 10px;
    margin-bottom: 0px;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 16px;
    margin-bottom: 25px;
}

div.stButton > button {
    width: 100%;
    min-height: 45px;
    border-radius: 12px;
    font-weight: 700;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎨 MISWAR\'S CREATORS AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI Chat • Image Understanding • Reference Image Editing'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "qwen_history" not in st.session_state:
    st.session_state.qwen_history = []

if "mode" not in st.session_state:
    st.session_state.mode = "AI Chat"


# ============================================================
# CLIENTS
# ============================================================

@st.cache_resource(show_spinner=False)
def get_chat_client():

    return Client(
        CHAT_SPACE,
        verbose=False
    )


@st.cache_resource(show_spinner=False)
def get_image_client():

    return Client(
        IMAGE_SPACE,
        verbose=False
    )


# ============================================================
# IMAGE HELPERS
# ============================================================

def open_uploaded_image(uploaded_file):

    return Image.open(
        BytesIO(
            uploaded_file.getvalue()
        )
    ).convert("RGB")


def save_temp_image(image):

    file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    )

    image.save(
        file.name,
        format="PNG"
    )

    file.close()

    return file.name


def image_bytes(image):

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


# ============================================================
# QWEN CHAT
# ============================================================

def qwen_chat(
    user_text,
    uploaded_file=None
):

    client = get_chat_client()

    # --------------------------------------------------------
    # Make a temporary image if supplied
    # --------------------------------------------------------

    temp_path = None

    if uploaded_file is not None:

        image = open_uploaded_image(
            uploaded_file
        )

        temp_path = save_temp_image(
            image
        )

        query = (
            temp_path,
        )

    else:

        query = user_text

    # --------------------------------------------------------
    # Add user message to Qwen history
    #
    # Official Qwen Space uses:
    # chatbot + task_history
    # --------------------------------------------------------

    if uploaded_file is not None:

        st.session_state.qwen_history.append(
            (query, None)
        )

    else:

        st.session_state.qwen_history.append(
            (user_text, None)
        )

    # --------------------------------------------------------
    # Build chatbot display history
    # --------------------------------------------------------

    chatbot_history = []

    for q, a in st.session_state.qwen_history:

        if isinstance(
            q,
            (tuple, list)
        ):

            if len(q) > 0:

                chatbot_history.append(
                    (
                        (q[0],),
                        a
                    )
                )

        else:

            chatbot_history.append(
                (
                    q,
                    a
                )
            )

    # --------------------------------------------------------
    # Current official endpoint
    # --------------------------------------------------------

    try:

        job = client.submit(
            chatbot_history,
            st.session_state.qwen_history,
            api_name="/predict"
        )

        result = job.result()

    except Exception:

        # Fallback to synchronous call
        result = client.predict(
            chatbot_history,
            st.session_state.qwen_history,
            api_name="/predict"
        )

    # --------------------------------------------------------
    # Official Space returns chatbot history
    # --------------------------------------------------------

    if isinstance(
        result,
        list
    ):

        if len(result) > 0:

            last = result[-1]

            if isinstance(
                last,
                (tuple, list)
            ) and len(last) >= 2:

                answer = last[1]

                if answer is None:
                    answer = ""

                answer = str(
                    answer
                )

            else:

                answer = str(
                    last
                )

        else:

            answer = ""

    else:

        answer = str(
            result
        )

    # --------------------------------------------------------
    # Update our local Qwen history with answer
    # --------------------------------------------------------

    if st.session_state.qwen_history:

        old_q, _ = (
            st.session_state.qwen_history[-1]
        )

        st.session_state.qwen_history[-1] = (
            old_q,
            answer
        )

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    if temp_path:

        try:
            os.remove(
                temp_path
            )
        except:
            pass

    return answer


# ============================================================
# IMAGE EDIT PROMPT
# ============================================================

def build_edit_prompt(
    user_prompt,
    ratio
):

    return f"""
Use the uploaded image as the PRIMARY visual reference.

IMPORTANT:

Preserve the reference image's important visual
characteristics unless the user specifically asks
to change them.

Pay very close attention to:

- clothing design
- dress structure
- silhouette
- exact colors
- color placement
- fabric appearance
- neckline
- sleeves
- embroidery
- patterns
- accessories
- styling
- person's overall appearance

Do not replace the reference outfit with an unrelated
random outfit.

If the user requests a new model, pose, background,
lighting or environment, make those changes while
preserving the requested clothing/design.

If the user says KEEP THE DRESS COLOR, preserve it.

USER REQUEST:

{user_prompt}

COMPOSITION:

Final image aspect ratio: {ratio}

QUALITY:

Photorealistic,
ultra detailed,
realistic skin,
realistic hair,
realistic fabric,
accurate garment construction,
sharp clothing details,
professional fashion photography,
premium editorial photography,
natural lighting,
realistic shadows,
high-end commercial image,
clean composition.

Do not add unnecessary objects.
Do not change important reference details
unless explicitly requested.
"""


# ============================================================
# QWEN IMAGE EDIT
# ============================================================

def qwen_image_edit(
    uploaded_file,
    prompt
):

    client = get_image_client()

    image = open_uploaded_image(
        uploaded_file
    )

    temp_path = save_temp_image(
        image
    )

    try:

        seed = random.randint(
            0,
            2147483647
        )

        # ----------------------------------------------------
        # CURRENT OFFICIAL QWEN IMAGE EDIT ENDPOINT
        # ----------------------------------------------------

        result = client.predict(

            handle_file(
                temp_path
            ),

            prompt,

            seed,

            True,

            4.0,

            50,

            True,

            api_name="/infer"
        )

        # ----------------------------------------------------
        # Official result:
        # [image, seed]
        # ----------------------------------------------------

        if isinstance(
            result,
            (list, tuple)
        ):

            generated = result[0]

        else:

            generated = result

        # ----------------------------------------------------
        # PIL
        # ----------------------------------------------------

        if isinstance(
            generated,
            Image.Image
        ):

            return generated.convert(
                "RGB"
            )

        # ----------------------------------------------------
        # File path
        # ----------------------------------------------------

        if isinstance(
            generated,
            str
        ):

            if os.path.exists(
                generated
            ):

                return Image.open(
                    generated
                ).convert(
                    "RGB"
                )

            # ------------------------------------------------
            # URL
            # ------------------------------------------------

            if generated.startswith(
                "http"
            ):

                import requests

                response = requests.get(
                    generated,
                    timeout=180
                )

                response.raise_for_status()

                return Image.open(
                    BytesIO(
                        response.content
                    )
                ).convert(
                    "RGB"
                )

        raise RuntimeError(
            "Qwen Image Edit returned an unexpected result."
        )

    finally:

        try:
            os.remove(
                temp_path
            )
        except:
            pass


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Studio Controls")

    # --------------------------------------------------------
    # MODE
    # --------------------------------------------------------

    st.subheader("🤖 AI Mode")

    mode = st.radio(
        "Choose what you want",
        [
            "AI Chat",
            "Image Understanding",
            "Reference Image Edit"
        ]
    )

    st.session_state.mode = mode

    st.divider()

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    st.subheader("🖼️ Upload Image")

    uploaded_files = st.file_uploader(
        "Upload image",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.success(
            f"✅ {len(uploaded_files)} image(s) uploaded"
        )

        for i, file in enumerate(
            uploaded_files[:3]
        ):

            st.image(
                file,
                caption=f"Reference {i + 1}",
                use_container_width=True
            )

    st.divider()

    # --------------------------------------------------------
    # RATIO
    # --------------------------------------------------------

    st.subheader("📐 Image Ratio")

    aspect_ratio = st.selectbox(
        "Select ratio",
        [
            "16:9",
            "9:16",
            "1:1",
            "4:5",
            "3:4",
            "4:3",
            "3:2",
            "2:3"
        ]
    )

    st.divider()

    # --------------------------------------------------------
    # REFERENCE
    # --------------------------------------------------------

    preserve_reference = st.checkbox(
        "🎯 Preserve reference design",
        value=True
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

        st.session_state.qwen_history = []

        st.rerun()


# ============================================================
# MODE DESCRIPTION
# ============================================================

if mode == "AI Chat":

    st.info(
        "💬 Normal AI conversation — ask questions, "
        "write prompts, SEO, coding, ideas, stories, etc."
    )

elif mode == "Image Understanding":

    st.info(
        "👁️ Upload an image and ask Qwen to describe "
        "or analyze it."
    )

else:

    st.info(
        "🎨 Upload a reference image and tell the AI "
        "what you want changed."
    )


# ============================================================
# DISPLAY OLD CHAT
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
    "Message Miswar's Creators..."
)


# ============================================================
# USER MESSAGE
# ============================================================

if user_prompt:

    st.session_state.messages.append(
        {
            "role":
                "user",

            "content":
                user_prompt
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            user_prompt
        )

    # ========================================================
    # ASSISTANT
    # ========================================================

    with st.chat_message(
        "assistant"
    ):

        # ====================================================
        # REFERENCE IMAGE EDIT
        # ====================================================

        if mode == "Reference Image Edit":

            if not uploaded_files:

                st.error(
                    "🖼️ Pehle reference image upload karo."
                )

                st.stop()

            try:

                with st.spinner(
                    "🎨 Qwen reference image ko process kar raha hai..."
                ):

                    final_prompt = build_edit_prompt(
                        user_prompt,
                        aspect_ratio
                    )

                    generated_image = qwen_image_edit(
                        uploaded_files[0],
                        final_prompt
                    )

                st.success(
                    "✅ Image ready!"
                )

                st.image(
                    generated_image,
                    use_container_width=True
                )

                st.download_button(
                    "⬇️ Download Image",
                    data=image_bytes(
                        generated_image
                    ),
                    file_name=
                        "miswars_creators.png",
                    mime="image/png",
                    use_container_width=True
                )

                answer = (
                    "✨ **Image Generated Successfully**\n\n"
                    f"**Aspect Ratio:** `{aspect_ratio}`\n\n"
                    "Reference image was used as the primary "
                    "visual reference."
                )

                st.markdown(
                    answer
                )

                st.session_state.messages.append(
                    {
                        "role":
                            "assistant",

                        "content":
                            answer,

                        "image":
                            generated_image
                    }
                )

            except Exception as e:

                st.error(
                    "❌ Image generation failed."
                )

                st.warning(
                    "Qwen's free ZeroGPU Space may be busy "
                    "or temporarily unavailable."
                )

                st.code(
                    str(e)
                )

        # ====================================================
        # CHAT / IMAGE UNDERSTANDING
        # ====================================================

        else:

            image_for_chat = None

            if (
                mode == "Image Understanding"
                and uploaded_files
            ):

                image_for_chat = (
                    uploaded_files[0]
                )

            try:

                with st.spinner(
                    "🤖 Qwen soch raha hai..."
                ):

                    if mode == "Image Understanding":

                        if image_for_chat:

                            chat_prompt = (
                                "Carefully analyze the uploaded image. "
                                "Describe what you see accurately. "
                                "Pay attention to clothing, colors, "
                                "people, objects, background, pose, "
                                "composition and important visual details. "
                                "Then answer the user's request:\n\n"
                                + user_prompt
                            )

                        else:

                            chat_prompt = user_prompt

                    else:

                        chat_prompt = user_prompt

                    answer = qwen_chat(
                        chat_prompt,
                        image_for_chat
                    )

                st.markdown(
                    answer
                )

                st.session_state.messages.append(
                    {
                        "role":
                            "assistant",

                        "content":
                            answer
                    }
                )

            except Exception as e:

                st.error(
                    "❌ Qwen chat temporarily unavailable."
                )

                st.warning(
                    "The public Qwen Space may be busy, "
                    "sleeping, or rate-limited."
                )

                st.code(
                    str(e)
                )
