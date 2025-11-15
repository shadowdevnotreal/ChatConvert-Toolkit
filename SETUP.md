# ChatConvert Toolkit - Setup Guide

## Quick Start

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/shadowdevnotreal/ChatConvert-Toolkit.git
cd ChatConvert-Toolkit

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app_streamlit.py
```

## Configuring API Keys (Optional)

ChatConvert Toolkit works perfectly fine without any API keys, using keyword-based analytics. However, you can optionally add a Groq API key for AI-powered analytics.

### 🚨 IMPORTANT SECURITY NOTE

**secrets.toml is ONLY for local development/testing!**

- ✅ **Local development**: Use secrets.toml to save your key
- ❌ **Public deployment**: DO NOT deploy with secrets.toml containing your key
- ⚠️ **Why?** If deployed, your API key would be used by ALL users and you'd pay for everyone's usage!

### Option 1: Using secrets.toml (LOCAL DEVELOPMENT ONLY)

⚠️ **WARNING**: Only use this when running the app locally on your computer for development/testing!

1. **Copy the example file:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Edit the secrets file:**
   ```bash
   nano .streamlit/secrets.toml
   # or use your preferred editor
   ```

3. **Add your API key:**
   ```toml
   [default]
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```

4. **Restart the app:**
   The app will automatically load your API key on startup.

5. **For deployment (Streamlit Cloud, etc.):**
   Add this to your secrets.toml to indicate production mode:
   ```toml
   deployed = true
   ```
   This will prevent the app from using secrets and require users to enter their own keys.

### Option 2: Manual Entry (RECOMMENDED for production)

Simply enter your API key in the sidebar when running the app.

**For public/deployed apps:**
- Each user should enter their own API key
- Keys are stored in session (temporary, lost on reload)
- Users only pay for their own usage

## Getting a Free Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account (no credit card required)
3. Navigate to the "API Keys" section
4. Click "Create API Key"
5. Copy your key

### Free Tier Benefits:
- 14,400 requests per day
- Analyze ~1,000 conversations daily
- No cost, no credit card needed

## Security Notes

- **Never commit** `.streamlit/secrets.toml` to git (it's in `.gitignore`)
- The example file (`.streamlit/secrets.toml.example`) is safe to commit
- Your API key is stored locally on your machine only

## Troubleshooting

### "No such file or directory: .streamlit/secrets.toml"

This is normal if you haven't created the secrets file yet. The app will work fine without it using keyword-based analytics.

### API Key Not Loading

1. Make sure the file is named exactly `secrets.toml` (not `secrets.toml.txt`)
2. Check that it's in the `.streamlit` directory
3. Verify the format matches the example
4. Restart the Streamlit app

### Still Having Issues?

Open an issue on [GitHub](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/issues)
