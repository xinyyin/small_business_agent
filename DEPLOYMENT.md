# Deployment Guide for Streamlit Cloud

## Setting up API Key in Streamlit Cloud

### Step 1: Get your OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key (you won't be able to see it again)

### Step 2: Configure Secrets in Streamlit Cloud

1. Go to your app on [Streamlit Cloud](https://share.streamlit.io)
2. Click on **"Manage app"** (three dots menu in the lower right)
3. Click on **"Secrets"** tab
4. Add your API key in the following format:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

**Important**: 
- Use TOML format (key-value pairs)
- Do NOT include quotes around the key value in the secrets editor
- The key should start with `sk-` or `sk-proj-`

### Step 3: Deploy

1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. The app will automatically deploy

## Local Development Setup

For local development, create a `.env` file in the `marketing-assistant` directory:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

Or use Streamlit's secrets file (for testing):

1. Create `.streamlit/secrets.toml`:
```bash
mkdir -p .streamlit
```

2. Add your key:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

**Note**: The `.streamlit/secrets.toml` file is already in `.gitignore` and won't be committed.

## How It Works

The code automatically checks for API key in this order:
1. **Streamlit Cloud Secrets** (`st.secrets["OPENAI_API_KEY"]`) - for deployed apps
2. **Environment Variable** (`OPENAI_API_KEY`) - for local development

This allows the same code to work in both environments without modification.

## Troubleshooting

### Error: "OPENAI_API_KEY not found"
- **Streamlit Cloud**: 
  - Make sure you've added the key in the Secrets section
  - Check that the key name is exactly `OPENAI_API_KEY` (case-sensitive)
  - Verify the format is correct TOML: `OPENAI_API_KEY = "sk-..."`
- **Local**: 
  - Check that `.env` file exists and contains `OPENAI_API_KEY=...`
  - Or check `.streamlit/secrets.toml` exists

### Error: "AuthenticationError"
- Verify your API key is correct
- Check that the key has sufficient credits/quota
- Ensure the key hasn't been revoked
- Try regenerating the key in OpenAI dashboard

### Error: "Module not found"
- Make sure `requirements.txt` includes all dependencies
- Streamlit Cloud will automatically install from `requirements.txt`
- Check that all imports are correct

## Security Notes

- ✅ **Never commit** `.env` or `.streamlit/secrets.toml` to Git
- ✅ These files are already in `.gitignore`
- ✅ Use Streamlit Cloud's Secrets for production deployment
- ✅ Rotate your API keys regularly
- ✅ Use different keys for development and production if possible

## Testing the Configuration

After setting up secrets, test your app:
1. Try a simple brand strategy request
2. Try generating a visual
3. Check the logs if there are any errors

If everything works, you're all set! 🎉
