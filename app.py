import streamlit as st
from gradio_client import Client, handle_file
from PIL import Image
from io import BytesIO
import requests
import tempfile
import os
import time
import random
import re


# ============================================================
# MISWAR'S CREATORS AI
# Chat + Vision + Reference Image Editing
# ============================================================

st.set_page_config(
    page_title="Miswar's Creators AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CONFIG
# ============================================================

QWEN_IMAGE_SPACE = "Qwen/Qwen-Image-Edit"

# Text/vision Space
QWEN_CHAT_SPACE = "Qwen/Qwen3-VL-235B-A22B-Instruct"


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
    font-size: 42px;
    font-weight: 900;
    color: #111;
    margin-top: 5px;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 16px;
    margin-bottom: 25px;
}

.status-box {
    padding: 12px;
    border-radius: 12px;
    background: #ffffff;
    border: 1px solid #e5e5e5;
}

div.stButton > button {
    width: 100%;
    border-radius: 12px;
    min-height: 45px;
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
    'Chat • Vision • Reference Image Editing • AI Studio'
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
            "👋 **Welcome to Miswar's Creators AI!**\n\n"
            "Main normal questions ka answer de sakta hoon, "
            "uploaded images ko samajh sakta hoon, aur "
            "reference images ko edit karne mein help kar sakta hoon."
        }
    ]


if "mode" not in st.session_state:
    st.session_state.mode = "AI Chat"


# ============================================================
# HELPERS
# ============================================================

def image_to_bytes(image):
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def load_pil_image(uploaded_file):
    return Image.open(
        BytesIO(uploaded_file.getvalue())
    ).convert("RGB")


def save_temp_image(image):
    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    )

    image.save(
        temp.name,
        format="PNG"
    )

    temp.close()

    return temp.name


# ============================================================
# QWEN IMAGE CLIENT
# ============================================================

@st.cache_resource(show_spinner=False)
def get_image_client():

    return Client(
        QWEN_IMAGE_SPACE,
        verbose=False
    )


# ============================================================
# QWEN IMAGE GENERATION
# ============================================================

def qwen_image_edit(
    image_path,
    prompt
):

    client = get_image_client()

    seed = random.randint(
        1,
        2147483647
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Current Qwen Image Edit public Space parameters
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
    # Extract image
    # --------------------------------------------------------

    generated = result

    if isinstance(
        result,
        (list, tuple)
    ):
        generated = result[0]

    # --------------------------------------------------------
    # Gradio file path
    # --------------------------------------------------------

    if isinstance(
        generated,
        str
    ):

        if os.path.exists(generated):

            return Image.open(
                generated
            ).convert("RGB")

        if generated.startswith("http"):

            response = requests.get(
                generated,
                timeout=180
            )

            response.raise_for_status()

            return Image.open(
                BytesIO(response.content)
            ).convert("RGB")

    # --------------------------------------------------------
    # PIL
    # --------------------------------------------------------

    if isinstance(
        generated,
        Image.Image
    ):

        return generated.convert("RGB")

    raise RuntimeError(
        "Qwen returned an unsupported result."
    )


# ============================================================
# BUILD IMAGE PROMPT
# ============================================================

def build_image_prompt(
    user_prompt,
    aspect_ratio,
    preserve_reference
):

    reference_rules = ""

    if preserve_reference:

        reference_rules = """
IMPORTANT REFERENCE IMAGE RULES:

The uploaded image is the PRIMARY reference.

Study the reference carefully.

Preserve the important visual characteristics,
especially:

- dress design
- garment structure
- silhouette
- exact color
- color placement
- fabric appearance
- neckline
- sleeves
- embroidery
- print
- accessories
- styling

DO NOT replace the reference outfit with an unrelated
random outfit.

If the user requests a different model, pose,
background, camera angle or environment, change only
those requested elements.

If the user says to keep the dress color unchanged,
KEEP THE ORIGINAL COLOR.

If the reference contains a complete outfit,
preserve its design accurately.
"""

    return f"""
{reference_rules}

USER REQUEST:

{user_prompt}

COMPOSITION:

Create the final image in {aspect_ratio} aspect ratio.

QUALITY:

Ultra realistic professional photography,
photorealistic human,
realistic skin,
realistic hair,
realistic fabric,
accurate clothing construction,
sharp garment details,
natural lighting,
realistic shadows,
premium fashion campaign photography,
high-end editorial photography,
clean professional composition.

Do not add unnecessary objects.

Do not change important reference details
unless specifically requested.
"""


# ============================================================
# CHAT / VISION BACKEND
# ============================================================

@st.cache_resource(show_spinner=False)
def get_chat_client():

    return Client(
        QWEN_CHAT_SPACE,
        verbose=False
    )


def qwen_chat(
    prompt,
    image_file=None
):

    client = get_chat_client()

    # --------------------------------------------------------
    # Prepare optional image
    # --------------------------------------------------------

    if image_file:

        image_path = save_temp_image(
            load_pil_image(image_file)
        )

        # Different public Space versions may expose
        # different API functions. Try common endpoints.
        attempts = [
            "/generate",
            "/chat",
            "/predict"
        ]

        last_error = None

        for endpoint in attempts:

            try:

                result = client.predict(
                    handle_file(image_path),
                    prompt,
                    api_name=endpoint
                )

                try:
                    os.remove(image_path)
                except:
                    pass

                return extract_text(result)

            except Exception as e:

                last_error = e

        try:
            os.remove(image_path)
        except:
            pass

        raise RuntimeError(
            f"Vision Space endpoint unavailable: {last_error}"
        )

    # --------------------------------------------------------
    # Text only
    # --------------------------------------------------------

    attempts = [
        "/generate",
        "/chat",
        "/predict"
    ]

    last_error = None

    for endpoint in attempts:

        try:

            result = client.predict(
                prompt,
                api_name=endpoint
            )

            return extract_text(result)

        except Exception as e:

            last_error = e

    raise RuntimeError(
        f"Chat Space endpoint unavailable: {last_error}"
    )


# ============================================================
# EXTRACT TEXT FROM GRADIO RESULT
# ============================================================

def extract_text(result):

    if isinstance(
        result,
        str
    ):

        return result

    if isinstance(
        result,
        dict
    ):

        for key in [
            "text",
            "output",
            "response",
            "content"
        ]:

            if key in result:

                return str(
                    result[key]
                )

    if isinstance(
        result,
        (list, tuple)
    ):

        for item in result:

            if isinstance(
                item,
                str
            ):

                return item

            if isinstance(
                item,
                dict
            ):

                text = extract_text(item)

                if text:
                    return text

    return str(result)


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
        "Choose mode",
        [
            "AI Chat",
            "Image Understanding",
            "Reference Image Edit"
        ],
        index=0
    )

    st.session_state.mode = mode

    st.divider()

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    st.subheader("🖼️ Image")

    uploaded_files = st.file_uploader(
        "Upload reference/image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.success(
            f"✅ {len(uploaded_files)} image(s)"
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
    # ASPECT RATIO
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

        st.rerun()


# ============================================================
# MODE INFORMATION
# ============================================================

if mode == "AI Chat":

    st.info(
        "💬 Ask anything — writing, ideas, coding, prompts, "
        "questions, explanations, etc."
    )

elif mode == "Image Understanding":

    st.info(
        "👁️ Upload an image and ask me what is in it, "
        "describe it, analyze it, or create a prompt from it."
    )

else:

    st.info(
        "🎨 Upload a reference image and describe exactly "
        "what you want changed."
    )


# ============================================================
# DISPLAY HISTORY
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
    "Message Miswar's Creators..."
)


# ============================================================
# PROCESS
# ============================================================

if user_prompt:

    # --------------------------------------------------------
    # Save user
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_prompt
        )

    # --------------------------------------------------------
    # Assistant
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        # ====================================================
        # IMAGE EDIT MODE
        # ====================================================

        if mode == "Reference Image Edit":

            if not uploaded_files:

                st.error(
                    "🖼️ Please upload a reference image first."
                )

                st.stop()

            image_path = None

            try:

                with st.spinner(
                    "🎨 Qwen is processing your reference..."
                ):

                    reference_image = load_pil_image(
                        uploaded_files[0]
                    )

                    image_path = save_temp_image(
                        reference_image
                    )

                    final_prompt = build_image_prompt(
                        user_prompt,
                        aspect_ratio,
                        preserve_reference
                    )

                    result_image = qwen_image_edit(
                        image_path,
                        final_prompt
                    )

                # --------------------------------------------
                # Show
                # --------------------------------------------

                st.success(
                    "✅ Image generated!"
                )

                st.image(
                    result_image,
                    use_container_width=True
                )

                # --------------------------------------------
                # Download
                # --------------------------------------------

                image_bytes = image_to_bytes(
                    result_image
                )

                st.download_button(
                    "⬇️ Download Image",
                    data=image_bytes,
                    file_name="miswars_creators.png",
                    mime="image/png",
                    use_container_width=True
                )

                response = (
                    f"✨ **Image Generated Successfully**\n\n"
                    f"**Mode:** Reference Image Edit  \n"
                    f"**Ratio:** {aspect_ratio}"
                )

                st.markdown(
                    response
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                        "image": result_image
                    }
                )

            except Exception as e:

                st.error(
                    "❌ Image generation could not be completed."
                )

                st.warning(
                    "The free Hugging Face GPU may be busy, "
                    "sleeping, or temporarily unavailable."
                )

                st.code(
                    str(e)
                )

            finally:

                if image_path:

                    try:
                        os.remove(
                            image_path
                        )
                    except:
                        pass

        # ====================================================
        # VISION / CHAT
        # ====================================================

        else:

            try:

                with st.spinner(
                    "🤖 Thinking..."
                ):

                    image_for_chat = None

                    if (
                        mode == "Image Understanding"
                        and uploaded_files
                    ):

                        image_for_chat = (
                            uploaded_files[0]
                        )

                    # ----------------------------------------
                    # Context
                    # ----------------------------------------

                    conversation_context = ""

                    recent_messages = (
                        st.session_state.messages[-8:]
                    )

                    for msg in recent_messages:

                        if msg["role"] in [
                            "user",
                            "assistant"
                        ]:

                            conversation_context += (
                                f"\n{msg['role'].upper()}: "
                                f"{msg['content']}"
                            )

                    system_instruction = """
You are Miswar's Creators AI.

Be helpful, natural, intelligent and conversational.

You can help with:

- general questions
- writing
- rewriting
- translations
- YouTube content
- SEO
- fashion prompts
- image prompts
- coding
- explanations
- brainstorming
- image analysis
- creative ideas

When the user uploads an image, carefully analyze it.

When the user asks for an image-generation prompt,
create a detailed professional prompt.

Respond naturally and clearly.

Do not claim that you generated an image unless the
image-generation mode actually generated one.
"""

                    final_chat_prompt = (
                        system_instruction
                        + "\n\nCONVERSATION:"
                        + conversation_context
                        + "\n\nCURRENT USER:"
                        + user_prompt
                    )

                    answer = qwen_chat(
                        final_chat_prompt,
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
                    "❌ AI chat service is temporarily unavailable."
                )

                st.warning(
                    "The public Hugging Face Space may be "
                    "sleeping, busy, or its API may have changed."
                )

                st.code(
                    str(e)
                )
