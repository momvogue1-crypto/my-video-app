import streamlit as st
import requests
import base64
import hashlib
import secrets
import urllib.parse
import random
import json

# ============================================================
# MISWAR'S CREATORS
# Pollinations BYOP + OAuth PKCE + Image Generation
# ============================================================

st.set_page_config(
    page_title="Miswar's Creators",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONFIG
# ============================================================

POLLINATIONS_AUTHORIZE_URL = (
    "https://enter.pollinations.ai/authorize"
)

POLLINATIONS_TOKEN_URL = (
    "https://enter.pollinations.ai/api/oauth/token"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/v1/images/edits"
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
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: #111111;
    margin-bottom: 4px;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 16px;
    margin-bottom: 28px;
}

.auth-box {
    padding: 18px;
    border-radius: 16px;
    background: white;
    border: 1px solid #dddddd;
    margin-bottom: 18px;
}

div.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
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
    'AI Image Studio • BYOP • Reference Images • HD Generation'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "messages": [],
    "access_token": None,
    "oauth_state": None,
    "pkce_verifier": None,
    "auth_started": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# LOAD APP KEY
# ============================================================

try:

    APP_KEY = st.secrets["POLLINATIONS_APP_KEY"]

except Exception:

    APP_KEY = ""


# ============================================================
# HELPER — BASE64URL
# ============================================================

def base64url_encode(data):

    return base64.urlsafe_b64encode(
        data
    ).rstrip(b"=").decode("ascii")


# ============================================================
# PKCE
# ============================================================

def create_pkce():

    verifier = base64url_encode(
        secrets.token_bytes(32)
    )

    challenge = base64url_encode(
        hashlib.sha256(
            verifier.encode("ascii")
        ).digest()
    )

    return verifier, challenge


# ============================================================
# CURRENT REDIRECT URI
# ============================================================

def get_redirect_uri():

    try:

        return st.context.url.split("?")[0]

    except Exception:

        return "http://localhost:8501"


REDIRECT_URI = get_redirect_uri()


# ============================================================
# CREATE AUTH URL
# ============================================================

def create_auth_url():

    verifier, challenge = create_pkce()

    state = secrets.token_urlsafe(32)

    st.session_state.pkce_verifier = verifier
    st.session_state.oauth_state = state
    st.session_state.auth_started = True

    params = {

        "response_type": "code",

        "client_id": APP_KEY,

        "redirect_uri": REDIRECT_URI,

        "scope": "usage",

        "state": state,

        "code_challenge": challenge,

        "code_challenge_method": "S256",

        # User can approve a budget on Pollinations screen.
        "budget": "5",

        # User-authorized token lifetime.
        "expiry": "7",
    }

    return (
        POLLINATIONS_AUTHORIZE_URL
        + "?"
        + urllib.parse.urlencode(params)
    )


# ============================================================
# HANDLE OAUTH CALLBACK
# ============================================================

def handle_oauth_callback():

    params = st.query_params

    code = params.get("code")
    returned_state = params.get("state")
    error = params.get("error")

    if error:

        st.error(
            f"Pollinations authorization failed: {error}"
        )

        return

    if not code:

        return

    # --------------------------------------------------------
    # STATE CHECK
    # --------------------------------------------------------

    expected_state = st.session_state.get(
        "oauth_state"
    )

    if not expected_state:

        st.error(
            "OAuth session expired. Please connect again."
        )

        return

    if returned_state != expected_state:

        st.error(
            "Security check failed: invalid OAuth state."
        )

        return

    # --------------------------------------------------------
    # VERIFIER
    # --------------------------------------------------------

    verifier = st.session_state.get(
        "pkce_verifier"
    )

    if not verifier:

        st.error(
            "PKCE session expired. Please connect again."
        )

        return

    # --------------------------------------------------------
    # TOKEN EXCHANGE
    # --------------------------------------------------------

    payload = {

        "grant_type":
            "authorization_code",

        "code":
            code,

        "client_id":
            APP_KEY,

        "redirect_uri":
            REDIRECT_URI,

        "code_verifier":
            verifier,
    }

    try:

        response = requests.post(
            POLLINATIONS_TOKEN_URL,
            data=payload,
            timeout=30
        )

        if response.status_code != 200:

            try:
                error_data = response.json()
            except Exception:
                error_data = response.text

            st.error(
                "Pollinations token exchange failed."
            )

            st.code(
                str(error_data)
            )

            return

        token_data = response.json()

        access_token = token_data.get(
            "access_token"
        )

        if not access_token:

            st.error(
                "No access token returned by Pollinations."
            )

            st.code(
                json.dumps(
                    token_data,
                    indent=2
                )
            )

            return

        # ----------------------------------------------------
        # SAVE USER TOKEN IN SESSION ONLY
        # ----------------------------------------------------

        st.session_state.access_token = (
            access_token
        )

        st.session_state.pkce_verifier = None
        st.session_state.oauth_state = None
        st.session_state.auth_started = False

        # Remove OAuth query params.
        st.query_params.clear()

        st.success(
            "✅ Pollinations connected successfully!"
        )

        st.rerun()

    except Exception as e:

        st.error(
            "OAuth connection error."
        )

        st.code(
            str(e)
        )


# ============================================================
# HANDLE CALLBACK BEFORE UI
# ============================================================

if APP_KEY:

    handle_oauth_callback()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Studio Controls")

    # ========================================================
    # BYOP CONNECTION
    # ========================================================

    st.subheader("🔐 Pollinations BYOP")

    if st.session_state.access_token:

        st.success(
            "🟢 Pollinations Connected"
        )

        st.caption(
            "Generation will use the user's authorized "
            "Pollinations balance."
        )

        if st.button(
            "🔓 Disconnect",
            use_container_width=True
        ):

            st.session_state.access_token = None

            st.rerun()

    else:

        if not APP_KEY:

            st.error(
                "POLLINATIONS_APP_KEY is missing."
            )

            st.info(
                "Add your pk_ App Key to "
                ".streamlit/secrets.toml"
            )

        else:

            auth_url = create_auth_url()

            st.link_button(
                "🔐 Connect Pollinations",
                auth_url,
                use_container_width=True
            )

            st.caption(
                "Users authorize their own Pollen. "
                "Your app does not use your personal API key."
            )

    st.divider()

    # ========================================================
    # REFERENCE IMAGES
    # ========================================================

    st.subheader("🖼️ Reference Images")

    uploaded_files = st.file_uploader(
        "Upload up to 6 reference images",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:

        if len(uploaded_files) > 6:

            st.warning(
                "Maximum 6 images allowed."
            )

            uploaded_files = uploaded_files[:6]

        st.success(
            f"✅ {len(uploaded_files)} image(s) attached"
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

    # ========================================================
    # MODEL
    # ========================================================

    st.subheader("🧠 AI Model")

    model = st.selectbox(
        "Image Model",
        [
            "nanobanana-2",
            "nanobanana",
            "nanobanana-pro",
            "seedream5",
            "gptimage-large",
            "gpt-image-2",
            "kontext",
            "p-image-edit",
            "flux"
        ],
        index=0
    )

    st.divider()

    # ========================================================
    # SIZE
    # ========================================================

    st.subheader("📐 Image Size")

    size_mapping = {

        "16:9 — YouTube Thumbnail":
            (1920, 1080),

        "9:16 — Shorts / Reels":
            (1080, 1920),

        "1:1 — Square":
            (1536, 1536),

        "4:5 — Instagram":
            (1080, 1350),

        "3:4 — Vertical":
            (1080, 1440),

        "4:5 — High Quality":
            (1536, 1920),
    }

    aspect_ratio_label = st.selectbox(
        "Aspect Ratio",
        list(size_mapping.keys())
    )

    width, height = size_mapping[
        aspect_ratio_label
    ]

    st.caption(
        f"{width} × {height}px"
    )

    st.divider()

    # ========================================================
    # QUALITY
    # ========================================================

    st.subheader("✨ Quality")

    quality = st.selectbox(
        "Quality",
        [
            "high",
            "medium",
            "low"
        ],
        index=0
    )

    # ========================================================
    # SEED
    # ========================================================

    random_seed = st.checkbox(
        "🎲 Random Seed",
        value=True
    )

    if random_seed:

        seed = random.randint(
            1,
            999999999
        )

    else:

        seed = st.number_input(
            "Seed",
            min_value=1,
            max_value=999999999,
            value=123456
        )

    st.divider()

    # ========================================================
    # CLEAR
    # ========================================================

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# IMAGE GENERATION
# ============================================================

def generate_image(
    prompt,
    access_token,
    model,
    width,
    height,
    quality,
    seed,
    reference_images
):

    headers = {

        "Authorization":
            f"Bearer {access_token}"
    }

    # --------------------------------------------------------
    # STRONG REFERENCE PROMPT
    # --------------------------------------------------------

    if reference_images:

        final_prompt = f"""
Use the uploaded reference image(s) as the PRIMARY
visual reference for this generation.

IMPORTANT REFERENCE RULES:

Study the reference image(s) carefully.

Preserve the important visual characteristics from
the reference whenever compatible with the user's request:

• clothing design
• dress structure
• garment silhouette
• neckline
• sleeves
• fabric appearance
• exact or very similar colors
• color placement
• embroidery
• patterns
• accessories
• styling
• proportions
• important visual details

Do NOT ignore the reference.

Do NOT create an unrelated design.

If the user asks for a change, make that change while
keeping the recognizable characteristics of the reference.

USER REQUEST:

{prompt}

QUALITY:

Photorealistic premium fashion photography,
high detail,
sharp garment texture,
realistic fabric,
accurate construction,
natural skin,
professional studio lighting,
cinematic but realistic lighting,
premium editorial photography,
clean composition,
high dynamic range,
commercial campaign quality.
"""

    else:

        final_prompt = f"""
{prompt}

Create a premium photorealistic image.

High detail,
sharp textures,
realistic materials,
professional photography,
natural lighting,
clean composition,
high dynamic range,
commercial quality.
"""

    # --------------------------------------------------------
    # MULTIPART IMAGES
    # --------------------------------------------------------

    files = []

    for reference in reference_images:

        files.append(
            (
                "image",
                (
                    reference.name,
                    reference.getvalue(),
                    reference.type or "image/png"
                )
            )
        )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    data = {

        "model":
            model,

        "prompt":
            final_prompt,

        "width":
            str(width),

        "height":
            str(height),

        "quality":
            quality,

        "seed":
            str(seed),
    }

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    response = requests.post(

        POLLINATIONS_IMAGE_URL,

        headers=headers,

        data=data,

        files=files if files else None,

        timeout=300
    )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if response.status_code != 200:

        try:

            error_data = response.json()

        except Exception:

            error_data = response.text

        raise RuntimeError(
            f"Pollinations API "
            f"{response.status_code}: "
            f"{error_data}"
        )

    # --------------------------------------------------------
    # IMAGE RESPONSE
    # --------------------------------------------------------

    content_type = (
        response.headers
        .get("content-type", "")
        .lower()
    )

    if "image" in content_type:

        return response.content

    # --------------------------------------------------------
    # JSON RESPONSE FALLBACK
    # --------------------------------------------------------

    try:

        result = response.json()

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
            f"Unexpected response: {result}"
        )

    except ValueError:

        raise RuntimeError(
            "Pollinations returned an unexpected response."
        )


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
# GENERATE
# ============================================================

if user_prompt:

    # --------------------------------------------------------
    # AUTH CHECK
    # --------------------------------------------------------

    if not st.session_state.access_token:

        st.error(
            "🔐 Please connect Pollinations first "
            "using the BYOP button in the sidebar."
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

        st.markdown(
            user_prompt
        )

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        status = st.empty()

        try:

            if uploaded_files:

                status.info(
                    "🖼️ Sending reference image(s) "
                    "to the image-edit model..."
                )

            else:

                status.info(
                    "🎨 Preparing generation..."
                )

            with st.spinner(
                "🔥 Miswar's Creators is rendering..."
            ):

                image_bytes = generate_image(

                    prompt=user_prompt,

                    access_token=
                        st.session_state.access_token,

                    model=model,

                    width=width,

                    height=height,

                    quality=quality,

                    seed=seed,

                    reference_images=
                        uploaded_files or []
                )

            status.empty()

            st.success(
                "✅ Image generated successfully!"
            )

            st.image(
                image_bytes,
                caption=(
                    f"{model} • "
                    f"{width}×{height}"
                ),
                use_container_width=True
            )

            # ------------------------------------------------
            # DOWNLOAD
            # ------------------------------------------------

            st.download_button(

                "⬇️ Download HD Image",

                data=image_bytes,

                file_name=
                    "miswars_creators_image.png",

                mime="image/png",

                use_container_width=True
            )

            # ------------------------------------------------
            # INFO
            # ------------------------------------------------

            info = (
                f"✨ **Generated Successfully**\n\n"
                f"**Model:** `{model}`  \n"
                f"**Size:** `{width} × {height}`  \n"
                f"**Quality:** `{quality}`  \n"
                f"**Seed:** `{seed}`"
            )

            if uploaded_files:

                info += (
                    f"  \n"
                    f"**References:** "
                    f"`{len(uploaded_files)}`"
                )

            st.markdown(info)

            st.session_state.messages.append(
                {
                    "role":
                        "assistant",

                    "content":
                        info,

                    "image_bytes":
                        image_bytes
                }
            )

        except Exception as e:

            status.empty()

            st.error(
                "❌ Generation failed."
            )

            st.code(
                str(e)
            )
