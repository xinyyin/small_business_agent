import base64
from io import BytesIO
import streamlit as st
from PIL import Image
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from agent import get_openai_api_key, chat_once, AgentState

st.set_page_config(
    page_title="Small Business Marketing Assistant", page_icon="📣"
)

api_key = get_openai_api_key()
if not api_key:
    st.error("""
    **API Key Not Configured**
    
    Please set your OpenAI API key:
    - **Streamlit Cloud**: Go to Manage app → Secrets and add:
      ```toml
      OPENAI_API_KEY = "sk-your-key-here"
      ```
    - **Local**: Create a `.env` file with:
      ```
      OPENAI_API_KEY=sk-your-key-here
      ```
    """)
    st.stop()

st.title("📣 Marketing Assistant for Small Business")

st.markdown(
    "This assistant helps small business owners design **brand strategy, marketing copy, "
    "and brand visuals** (posters/logos/hero images)."
)

st.sidebar.header("Business Profile")
business_type = st.sidebar.text_input(
    "Business type", placeholder="e.g. specialty coffee shop"
)
target_audience = st.sidebar.text_input(
    "Target audience", placeholder="e.g. college students nearby"
)
brand_tone = st.sidebar.selectbox(
    "Brand tone",
    ["Warm & friendly", "Minimal & calm", "Playful & bold", "Luxury & elegant"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.header("📁 Upload Documents for RAG")

uploaded_files = st.sidebar.file_uploader(
    "Upload brand case studies or documents",
    type=["txt", "md"],
    accept_multiple_files=True,
    help="Upload .txt or .md files to enhance the RAG knowledge base"
)

if uploaded_files:
    from rag import BrandRAG
    
    if "brand_rag" not in st.session_state:
        st.session_state["brand_rag"] = BrandRAG(
            folder="data/brand_cases", 
            openai_api_key=api_key
        )
    
    if "processed_files" not in st.session_state:
        st.session_state["processed_files"] = set()
    
    rag = st.session_state["brand_rag"]
    
    for uploaded_file in uploaded_files:
        if uploaded_file is not None and uploaded_file.name not in st.session_state["processed_files"]:
            file_content = uploaded_file.read()
            rag.add_file(file_content, uploaded_file.name)
            st.session_state["processed_files"].add(uploaded_file.name)
            st.sidebar.success(f"✅ Added: {uploaded_file.name}")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "ℹ️ You can also add case studies as `.txt` / `.md` files under "
    "`data/brand_cases/` folder."
)

with st.sidebar.expander("⚠️ Responsible AI & Limitations"):
    st.markdown("""
    **This tool:**
    - Provides marketing suggestions, not legal/financial advice
    - Generates conceptual visuals - verify copyright/trademark before use
    - Requires human review of all AI-generated content
    
    **You are responsible for:**
    - Ensuring compliance with advertising regulations
    - Verifying claims and statistics
    - Customizing content for your specific business
    - Checking trademark/copyright for generated visuals
    """)

if "messages" not in st.session_state:
    st.session_state["messages"]: list[BaseMessage] = []

if "last_image" not in st.session_state:
    st.session_state["last_image"] = ""

for msg in st.session_state["messages"]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

if st.session_state["last_image"]:
    try:
        img_bytes = base64.b64decode(st.session_state["last_image"])
        img = Image.open(BytesIO(img_bytes))
        st.image(img, caption="Generated marketing visual", use_container_width=True)
    except Exception:
        pass

user_input = st.chat_input(
    "Describe what you need help with (e.g., brand positioning, IG captions, or a hero visual)..."
)

if user_input:
    profile_lines = []
    if business_type:
        profile_lines.append(f"Business type: {business_type}")
    if target_audience:
        profile_lines.append(f"Target audience: {target_audience}")
    if brand_tone:
        profile_lines.append(f"Brand tone: {brand_tone}")

    if profile_lines:
        enriched = (
            "Here is my business profile:\n"
            + "\n".join(profile_lines)
            + "\n\nNow my request:\n"
            + user_input
        )
    else:
        enriched = user_input

    with st.chat_message("user"):
        st.write(user_input)

    history: list[BaseMessage] = st.session_state["messages"]
    new_state: AgentState = chat_once(enriched, history)

    st.session_state["messages"] = new_state["messages"]
    st.session_state["last_image"] = new_state.get("image_b64", "")

    last_msg = new_state["messages"][-1]
    if isinstance(last_msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(last_msg.content)

    if st.session_state["last_image"]:
        try:
            img_bytes = base64.b64decode(st.session_state["last_image"])
            img = Image.open(BytesIO(img_bytes))
            st.image(img, caption="Generated marketing visual", use_container_width=True)
        except Exception:
            pass

