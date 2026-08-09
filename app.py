import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64
import os


# ============================================================
# MISWAR'S CREATORS AI
# OPENAI VERSION
# Chat + Vision + Image Generation + Image Editing
# ============================================================

st.set_page_config(
    page_title="Miswar's Creators AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_api_key():

    # Streamlit Secrets
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    # Environment variable
    key = os.getenv("OPENAI_API_KEY")

    return key


API_KEY = get_api_key()

if API_KEY:
    client = OpenAI(api_key=API_KEY)
else:
    client = None


# ============================================================
# PAGE CSS
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
    'Powered by OpenAI • Chat • Vision • Image Creation'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "AI Chat"


# ============================================================
# IMAGE HELPERS
# ============================================================

def load_image(uploaded_file):

    return Image.open(
        BytesIO(
            uploaded_file.getvalue()
        )
    ).convert("RGB")


def image_to_bytes(image):

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


def image_to_data_url(uploaded_file):

    data = uploaded_file.getvalue()

    mime = uploaded_file.type or "image/png"

    encoded = base64.b64encode(
        data
    ).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


# ============================================================
# ASPECT RATIO → OPENAI SIZE
# ============================================================

def get_image_size(ratio):

    # GPT Image uses supported output sizes.
    # We map user's ratio to closest supported landscape,
    # portrait or square format.

    if ratio == "16:9":
        return "1536x1024"

    if ratio == "9:16":
        return "1024x1536"

    if ratio == "4:5":
        return "1024x1536"

    if ratio == "3:4":
        return "1024x1536"

    if ratio == "2:3":
        return "1024x1536"

    if ratio == "4:3":
        return "1536x1024"

    if ratio == "3:2":
        return "1536x1024"

    return "1024x1024"


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are Miswar's Creators AI.

You are a highly capable creative assistant.

Help the user with:

- normal conversation
- questions and answers
- writing
- rewriting
- translation
- YouTube content
- SEO
- titles
- descriptions
- tags
- fashion content
- image prompts
- creative ideas
- coding
- explanations
- brainstorming
- image analysis

Be friendly, direct and useful.

When the user uploads an image:
carefully analyze the image and answer based on what
is actually visible.

When the user asks for an image prompt:
write a detailed professional prompt.

Do not claim that an image was generated unless
the image generation function actually generated it.
"""


# ============================================================
# CHAT FUNCTION
# ============================================================

def ask_openai(
    prompt,
    uploaded_file=None
):

    if client is None:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    content = []

    content.append(
        {
            "type": "input_text",
            "text": prompt
        }
    )

    if uploaded_file is not None:

        image_url = image_to_data_url(
            uploaded_file
        )

        content.append(
            {
                "type": "input_image",
                "image_url": image_url
            }
        )

    response = client.responses.create(

        model="gpt-5",

        instructions=SYSTEM_INSTRUCTION,

        input=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return response.output_text


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image(
    prompt,
    ratio
):

    if client is None:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    size = get_image_size(
        ratio
    )

    final_prompt = f"""
Create a professional high-quality image.

USER REQUEST:
{prompt}

ASPECT RATIO:
{ratio}

QUALITY REQUIREMENTS:

Photorealistic,
ultra detailed,
professional photography,
realistic skin,
realistic hair,
realistic fabric,
accurate clothing construction,
sharp details,
natural lighting,
realistic shadows,
premium commercial photography,
high-end editorial quality,
clean composition.

Do not add unnecessary objects.
Follow the user's request exactly.
"""

    result = client.images.generate(

        model="gpt-image-1",

        prompt=final_prompt,

        size=size,

        quality="high"
    )

    image_base64 = (
        result.data[0].b64_json
    )

    image_bytes_data = base64.b64decode(
        image_base64
    )

    return Image.open(
        BytesIO(
            image_bytes_data
        )
    ).convert("RGB")


# ============================================================
# IMAGE EDITING
# ============================================================

def edit_image(
    uploaded_file,
    prompt,
    ratio
):

    if client is None:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    size = get_image_size(
        ratio
    )

    image_bytes_data = uploaded_file.getvalue()

    # --------------------------------------------------------
    # Preserve original reference
    # --------------------------------------------------------

    final_prompt = f"""
Use the uploaded image as the PRIMARY REFERENCE.

USER REQUEST:

{prompt}

REFERENCE PRESERVATION:

Preserve the important details of the reference
unless the user explicitly requests a change.

Pay special attention to:

- exact dress design
- garment structure
- silhouette
- original colors
- color placement
- fabric
- neckline
- sleeves
- embroidery
- patterns
- accessories
- styling

If the user says to keep the dress color,
DO NOT change the dress color.

If the user requests a different model,
change the model but preserve the requested outfit.

If the user requests a different background,
change the background while preserving the subject.

If the user requests a different pose,
change only the pose while preserving the outfit.

Create a realistic professional final image.
"""

    result = client.images.edit(

        model="gpt-image-1",

        image=BytesIO(
            image_bytes_data
        ),

        prompt=final_prompt,

        size=size
    )

    image_base64 = (
        result.data[0].b64_json
    )

    decoded = base64.b64decode(
        image_base64
    )

    return Image.open(
        BytesIO(
            decoded
        )
    ).convert("RGB")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Studio Controls")

    # --------------------------------------------------------
    # API STATUS
    # --------------------------------------------------------

    if API_KEY:

        st.success(
            "🟢 OpenAI API Connected"
        )

    else:

        st.error(
            "🔴 OpenAI API Key Missing"
        )

        st.caption(
            "Add OPENAI_API_KEY in Streamlit Secrets."
        )

    st.divider()

    # --------------------------------------------------------
    # MODE
    # --------------------------------------------------------

    st.subheader("🤖 AI Mode")

    mode = st.radio(
        "Choose mode",
        [
            "AI Chat",
            "Image Understanding",
            "Image Generation",
            "Reference Image Edit"
        ]
    )

    st.session_state.mode = mode

    st.divider()

    # --------------------------------------------------------
    # IMAGE UPLOAD
    # --------------------------------------------------------

    st.subheader("🖼️ Reference Image")

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
            f"✅ {len(uploaded_files)} image(s)"
        )

        for i, file in enumerate(
            uploaded_files[:6]
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
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MODE INFO
# ============================================================

if mode == "AI Chat":

    st.info(
        "💬 GPT Chat — normal conversation, coding, "
        "writing, SEO, ideas, prompts and more."
    )

elif mode == "Image Understanding":

    st.info(
        "👁️ Upload an image and ask GPT to analyze it."
    )

elif mode == "Image Generation":

    st.info(
        "🎨 Create a completely new image from your prompt."
    )

else:

    st.info(
        "🎯 Upload a reference image and tell GPT exactly "
        "what you want changed."
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
    "Message Miswar's Creators..."
)


# ============================================================
# PROCESS USER MESSAGE
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

        try:

            # ==================================================
            # NORMAL CHAT
            # ==================================================

            if mode == "AI Chat":

                with st.spinner(
                    "🤖 GPT is thinking..."
                ):

                    answer = ask_openai(
                        user_prompt
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


            # ==================================================
            # IMAGE UNDERSTANDING
            # ==================================================

            elif mode == "Image Understanding":

                if not uploaded_files:

                    st.warning(
                        "🖼️ Please upload an image first."
                    )

                    st.stop()

                with st.spinner(
                    "👁️ GPT is analyzing the image..."
                ):

                    answer = ask_openai(
                        user_prompt,
                        uploaded_files[0]
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


            # ==================================================
            # IMAGE GENERATION
            # ==================================================

            elif mode == "Image Generation":

                with st.spinner(
                    "🎨 GPT Image is creating your image..."
                ):

                    generated = generate_image(
                        user_prompt,
                        aspect_ratio
                    )

                st.success(
                    "✅ Image generated!"
                )

                st.image(
                    generated,
                    use_container_width=True
                )

                st.download_button(
                    "⬇️ Download Image",
                    data=image_to_bytes(
                        generated
                    ),
                    file_name=
                        "miswars_creators_ai.png",
                    mime="image/png",
                    use_container_width=True
                )

                answer = (
                    "✨ **Image Generated Successfully!**\n\n"
                    f"**Ratio:** `{aspect_ratio}`"
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
                            generated
                    }
                )


            # ==================================================
            # REFERENCE IMAGE EDIT
            # ==================================================

            elif mode == "Reference Image Edit":

                if not uploaded_files:

                    st.warning(
                        "🖼️ Please upload a reference image first."
                    )

                    st.stop()

                with st.spinner(
                    "🎨 GPT Image is editing your reference..."
                ):

                    edited = edit_image(
                        uploaded_files[0],
                        user_prompt,
                        aspect_ratio
                    )

                st.success(
                    "✅ Reference image edited!"
                )

                st.image(
                    edited,
                    use_container_width=True
                )

                st.download_button(
                    "⬇️ Download Edited Image",
                    data=image_to_bytes(
                        edited
                    ),
                    file_name=
                        "miswars_creators_edited.png",
                    mime="image/png",
                    use_container_width=True
                )

                answer = (
                    "✨ **Reference Image Edited Successfully!**\n\n"
                    f"**Ratio:** `{aspect_ratio}`"
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
                            edited
                    }
                )


        except Exception as e:

            st.error(
                "❌ OpenAI request failed."
            )

            error_text = str(e)

            if (
                "api_key" in error_text.lower()
                or "authentication" in error_text.lower()
                or "401" in error_text
            ):

                st.warning(
                    "🔑 OpenAI API key missing or invalid."
                )

            elif (
                "quota" in error_text.lower()
                or "billing" in error_text.lower()
            ):

                st.warning(
                    "💳 OpenAI API billing/quota issue. "
                    "Check your API account."
                )

            else:

                st.warning(
                    "Please check the error below."
                )

            st.code(
                error_text
            )
