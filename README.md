# AI Small Business Marketing Assistant
Demo: https://xinyyin-small-business-agent-app-fsllct.streamlit.app/
## 1. Motivation

Last quarter, I took a Product Management course where I designed a product for small business owners who struggle with marketing and branding. Many of them:

- don't have budget for professional agencies,
- feel overwhelmed by social media and brand strategy,
- but still need to create a consistent, compelling brand presence.

For this Generative AI course, I decided to turn that PM concept into a working prototype:

an AI assistant that helps small business owners:

- clarify their brand positioning and tone,
- generate tailored marketing copy (e.g., IG captions, headlines, campaign ideas),
- and even generate brand visuals (posters / hero images / logo-style graphics) purely using AI.

This project is built with the following technologies:

**RAG, embeddings, LangGraph agents, Streamlit, and image generation**, plus
responsible AI considerations.

## 2. How to Run
### 2.0 Access the deployed demo app

I deployed the app to Streamlit Cloud, you can access it [here](https://xinyyin-small-business-agent-app-fsllct.streamlit.app/).

### 2.1 If you want to run the app locally, you can follow the steps below.
### 2.1 Setup

```bash
git clone git@github.com:xinyyin/small_business_agent.git
cd marketing-assistant

python -m venv .venv
source .venv/bin/activate 

pip install -r requirements.txt
```

Set OpenAI API key in environment variables:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"

```

### 2.2 (Optional) Add Case Studies for RAG

Create a folder:

```bash
mkdir -p data/brand_cases
```

Add some `.txt` or `.md` files describing small business marketing case studies, for example:

- `coffee_shop_story.txt`
- `yoga_studio_launch.md`

If you don't add any files, the assistant will still work, just without grounded case-study references.

### 2.3 Run the App

```bash
streamlit run app.py
```