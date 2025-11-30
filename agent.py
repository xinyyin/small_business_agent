from typing import List, TypedDict, Optional
import os
import base64
import io
import requests
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langgraph.graph import StateGraph, END
from PIL import Image
from rag import BrandRAG

load_dotenv()

def get_openai_api_key() -> str:
    """Get OpenAI API key from Streamlit secrets or environment variable."""
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            try:
                if "OPENAI_API_KEY" in st.secrets:
                    key = st.secrets["OPENAI_API_KEY"]
                    if key and len(key.strip()) > 0:
                        return key.strip()
            except Exception as e:
                pass
    except Exception:
        pass
    env_key = os.environ.get("OPENAI_API_KEY", "")
    if env_key:
        return env_key.strip()
    return ""

class AgentState(TypedDict):
    messages: List[BaseMessage]
    image_b64: str

def get_client():
    """Get OpenAI client with API key from secrets or env."""
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. "
            "Please set it in Streamlit Cloud Secrets or as an environment variable."
        )
    return OpenAI(api_key=api_key)

def get_llm():
    """Get ChatOpenAI LLM with API key from secrets or env."""
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. "
            "Please set it in Streamlit Cloud Secrets or as an environment variable."
        )
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=api_key,
    )

def get_brand_rag():
    """Get BrandRAG instance with API key from secrets or env."""
    api_key = get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. "
            "Please set it in Streamlit Cloud Secrets or as an environment variable."
        )
    return BrandRAG(folder="data/brand_cases", openai_api_key=api_key)

BRAND_SYSTEM_PROMPT = """
You are an AI marketing strategist for small businesses.

ETHICAL GUIDELINES - You MUST follow these:
- Never make false or unsubstantiated claims about product performance, results, or guarantees
- Do not create content that discriminates against any group based on race, gender, age, religion, or other protected characteristics
- Avoid manipulative or deceptive marketing tactics
- Respect privacy - do not suggest collecting or using personal data without consent
- Be transparent about limitations - if you don't have specific information, state it clearly

ACCURACY GUIDELINES:
- Always think step by step
- Use brand case studies as *inspiration*, not as text to copy
- Tailor your advice to the specific business type, target audience, and brand tone
- Produce concrete, actionable suggestions (e.g., sample headlines, IG captions, campaign ideas)
- Prefer warm, encouraging, yet honest language

CONTEXT HANDLING:
- If I provide you with RAG context, treat it as privileged insights and ground your suggestions in it
- If the context is missing or not relevant, you MUST explicitly state: "I'm providing general marketing advice since I don't have specific case studies for your business type"
- Never invent specific facts, statistics, or case study details that weren't provided
"""

VISION_SYSTEM_PROMPT = """
You are a brand visual designer AI.

ETHICAL CONSTRAINTS:
- Do not create images that could be offensive, discriminatory, or inappropriate
- Avoid suggesting visuals that mislead consumers about product quality or features
- Do not include text in image descriptions that makes false claims
- Ensure visual descriptions are appropriate for all audiences

Your job is to create a *detailed image prompt* for a marketing visual based on:
- the user's business profile
- their request
- their desired brand tone
- optional case-study context

Your output must be ONLY the image prompt text, no extra commentary.

Describe:
- mood & emotional tone
- color palette
- composition & layout
- textures / materials
- lighting
- typography *feel* (but do NOT specify actual text)
- style (illustration vs photography, realism vs stylized)
- any relevant artistic influences
"""

def route(state: AgentState) -> str:
    messages = state["messages"]
    if not messages:
        return "brand"

    last = messages[-1]
    content = last.content.lower() if isinstance(last, HumanMessage) else ""

    image_keywords = [
        "visual",
        "image",
        "poster",
        "logo",
        "banner",
        "graphic",
        "design",
        "picture",
        "illustration",
    ]

    if any(kw in content for kw in image_keywords):
        return "vision"
    return "brand"


def brand_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    user_query = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_query = msg.content
            break

    brand_rag = get_brand_rag()
    rag_context, _ = brand_rag.search(user_query) if user_query else ("", [])
    prompt_messages: List[BaseMessage] = [SystemMessage(content=BRAND_SYSTEM_PROMPT)]

    if rag_context:
        prompt_messages.append(
            HumanMessage(
                content=(
                    "Here is relevant brand knowledge and case studies:\n\n"
                    f"{rag_context}\n\n"
                    "Please use these as inspiration and reference."
                )
            )
        )

    prompt_messages.extend(messages)
    llm = get_llm()
    resp = llm.invoke(prompt_messages)
    return AgentState(
        messages=messages + [resp], image_b64=state.get("image_b64", "")
    )


def vision_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    prompt_messages: List[BaseMessage] = [SystemMessage(content=VISION_SYSTEM_PROMPT)]
    prompt_messages.extend(messages)

    llm = get_llm()
    vision_prompt_msg = llm.invoke(prompt_messages)
    vision_prompt = vision_prompt_msg.content

    try:
        client = get_client()
        img_result = client.images.generate(
            model="dall-e-3",
            size="1024x1024",
            prompt=vision_prompt,
            n=1,
        )
        img_url = img_result.data[0].url
        img_response = requests.get(img_url)
        img = Image.open(io.BytesIO(img_response.content))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        b64 = base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"Error generating image: {e}")
        b64 = ""

    caption = (
        "I generated a marketing visual based on the following image prompt:\n\n"
        f"{vision_prompt}"
    )
    ai_msg = AIMessage(content=caption)
    return AgentState(messages=messages + [ai_msg], image_b64=b64)


def build_graph():
    graph = StateGraph(AgentState)

    def router_node(state: AgentState) -> AgentState:
        return state

    graph.add_node("router", router_node)
    graph.add_node("brand", brand_node)
    graph.add_node("vision", vision_node)
    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route,
        {
            "brand": "brand",
            "vision": "vision",
        },
    )

    graph.add_edge("brand", END)
    graph.add_edge("vision", END)
    return graph.compile()

assistant_graph = build_graph()

def chat_once(user_message: str, history: List[BaseMessage]) -> AgentState:
    state: AgentState = AgentState(
        messages=history + [HumanMessage(content=user_message)],
        image_b64="",
    )
    new_state: AgentState = assistant_graph.invoke(state)
    return new_state

