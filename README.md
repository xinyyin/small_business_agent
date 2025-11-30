# AI Small Business Marketing Assistant

## 1. Motivation

Last quarter, I took a Product Management course where I designed a product for **small business owners who struggle with marketing and branding**. Many of them:

- don't have budget for professional agencies,
- feel overwhelmed by social media and brand strategy,
- but still need to create a consistent, compelling brand presence.

For this Generative AI course, I decided to **turn that PM concept into a working prototype**:

an AI assistant that helps small business owners:

- clarify their brand positioning and tone,
- generate tailored marketing copy (e.g., IG captions, headlines, campaign ideas),
- and even **generate brand visuals (posters / hero images / logo-style graphics) purely using AI**.

This project is built to explicitly showcase the techniques we discussed in class:

**RAG, embeddings, LangGraph agents, Streamlit, and image generation**, plus
responsible AI considerations.

---

## 2. High-Level Architecture

```text
                ┌─────────────────────────┐
                │       User (Browser)    │
                │  - provide business info│
                │  - ask for copy/visuals │
                └──────────┬──────────────┘
                           │
                      (Streamlit UI)
                           │
            ┌──────────────▼────────────────┐
            │        app.py (Streamlit)     │
            │  - chat-style interface       │
            │  - collects business profile  │
            │  - calls LangGraph agent      │
            └───────────┬───────────────────┘
                        │ .invoke()
                        │
            ┌───────────▼───────────────────┐
            │    LangGraph Agent (agent.py) │
            │  - State: messages + image    │
            │  - router: brand vs vision    │
            │  - brand node: RAG + LLM      │
            │  - vision node: LLM prompt →  │
            │    OpenAI Images API          │
            └───────┬───────────┬──────────┘
                    │           │
             (RAG text)   (AI-only images)
                    │           │
      ┌─────────────▼───────┐   │
      │   RAG + FAISS (rag) │   │
      │ - load case studies │   │
      │ - embeddings + FAISS│   │
      │ - cosine similarity │   │
      └───────────┬─────────┘   │
                  │             │
          ┌───────▼───────┐     │
          │ brand_cases/  │     │
          │ (optional txt │     │
          │  & md files)  │     │
          └───────────────┘     │
                                │
                         ┌──────▼─────────┐
                         │ OpenAI Images  │
                         │ (dall-e-3)     │
                         └───────────────┘
```

## 3. Techniques from Class

This project is explicitly designed to use topics from the Generative AI lectures:

### 3.1 Prompt Engineering (Lecture 4)

- Separate system prompts for:
  - Brand strategy & copywriting (`BRAND_SYSTEM_PROMPT`)
  - Brand visual design (`VISION_SYSTEM_PROMPT`)
- Clear instructions (tone, structure, chain-of-thought).
- Business profile (type, audience, tone) is injected into the prompt.

### 3.2 RAG & Embeddings (Lecture 7)

`rag.py` implements a small RAG layer:

- loads `.txt` / `.md` case studies from `data/brand_cases/`
- splits them into chunks
- builds a FAISS vector store using OpenAI embeddings

For brand-strategy queries, the agent:

- retrieves relevant case-study snippets by cosine similarity,
- passes them as extra context to the LLM,
- and uses them as inspiration, not as text to copy.

If no documents are present, RAG gracefully degrades and the assistant answers more generally.

### 3.3 LangGraph Agents (Lecture 5/8)

The agent is implemented as a LangGraph `StateGraph`:

- **AgentState** holds:
  - `messages`: full chat history
  - `image_b64`: optionally, the last generated image
- **router node**:
  - inspects the latest user message
  - chooses between a `brand` node (text strategy/copy) and a `vision` node (visuals)
- **brand node**:
  - uses RAG + LLM to produce grounded marketing advice.
- **vision node**:
  - uses an LLM to create a detailed mid-level image prompt
  - calls the OpenAI Images API to produce an actual marketing visual.

### 3.4 Image Generation (Lecture 6)

- No local image data is required.
- The system uses AI-only image generation via `dall-e-3`:
  - The LLM acts as a "visual prompt engineer".
  - The image model turns that into a marketing visual (for hero images, posters, etc.).

### 3.5 Streamlit Frontend (Lecture 5)

A simple but functional single-page chat UI:

- **Sidebar**: business type, target audience, brand tone.
- **Chat**: user enters high-level marketing or visual requests.
- The assistant responds with:
  - textual strategy/copy, and
  - optionally, a generated marketing visual.

### 3.6 Responsible AI (Lecture 3)

The assistant is designed with several safety considerations:

- **No hallucinated facts about the business**:
  - The model explicitly uses user-provided profile + RAG context;
  - If context is missing, it must state that it's answering more generally.
- **Ethical marketing**:
  - No misleading claims about product performance.
  - No discriminatory or harmful targeting.
- **AI-generated visuals**:
  - Treated as conceptual mockups, not final production assets.
  - The README clarifies that users are responsible for checking trademark/copyright issues.

## 4. How to Run

### 4.1 Setup

```bash
git clone <your-repo-url>
cd marketing-assistant

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"

# Windows (PowerShell):
# $env:OPENAI_API_KEY="YOUR_KEY_HERE"
```

### 4.2 (Optional) Add Case Studies for RAG

Create a folder:

```bash
mkdir -p data/brand_cases
```

Add some `.txt` or `.md` files describing small business marketing case studies, for example:

- `coffee_shop_story.txt`
- `yoga_studio_launch.md`
- `florist_valentines_campaign.txt`

If you don't add any files, the assistant will still work, just without grounded case-study references.

### 4.3 Run the App

```bash
streamlit run app.py
```

Open the URL shown in your terminal (usually `http://localhost:8501`).

## 5. Example Interactions

### 5.1 Brand Positioning

**User:**
- Business type: specialty coffee shop
- Target audience: college students
- Brand tone: warm & friendly
- "Can you help me define a brand positioning and 3 key messages?"

→ The agent retrieves (if available) relevant coffee-shop case studies, then returns:
- A short brand positioning statement.
- 3–5 key brand messages.
- Example headlines / IG captions.

### 5.2 AI-Generated Visuals

**User:**
- "Please generate a hero visual for my coffee shop homepage – something cozy and minimal."

→ The agent:
- Uses `VISION_SYSTEM_PROMPT` to write a detailed image prompt.
- Calls `dall-e-3` to generate a 1024×1024 marketing visual.
- The Streamlit UI displays the image directly.

## 6. Limitations & Future Work

- **No persistent memory**: Conversations are session-local; there is no long-term memory across sessions.
- **No automatic dataset creation yet**: Currently, case studies are manually added as `.txt` / `.md` files. A natural extension would be:
  - Using the LLM to synthesize realistic case studies based on vertical (e.g., "10 creative florist campaigns").
- **No explicit MCP integration**: The architecture is ready to be extended with MCP for:
  - external data sources (e.g. live competitor research),
  - additional tools (posting to social media, etc.).

## 7. Files Overview

- `app.py` — Streamlit frontend.
- `agent.py` — LangGraph agent (router + brand node + vision node).
- `rag.py` — RAG + FAISS pipeline for text case studies.
- `requirements.txt` — Python dependencies.

If you have any questions about the architecture or want to extend it (e.g., add MCP tools, more complex LangGraph workflows, or more advanced safety filters), feel free to iterate on this base.

