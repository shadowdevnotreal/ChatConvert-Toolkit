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

**The app is designed so each user must enter their own API key!**

- ✅ **Owner/Developer Testing**: Use secrets.toml (local) or Streamlit Cloud Secrets UI (deployed)
- ✅ **End Users**: Must enter their own API key in the sidebar
- 🔒 **How it works**: The app code NEVER uses secrets for end users - only for your own testing
- ⚠️ **Important**: Secrets are for YOUR testing convenience only, not for end users

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
   Your API key will be available for your own testing. End users will still need to enter their own keys.

5. **For Streamlit Cloud deployment:**
   - Use the Streamlit Cloud Secrets UI instead of secrets.toml
   - Go to: App Settings → Secrets → Add your key there
   - This is for YOUR testing only when you're signed into Streamlit Cloud
   - End users will still see the API key input field and must provide their own keys
   - Documentation: [Streamlit Secrets Management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

### Option 2: Manual Entry (REQUIRED for end users)

All end users must enter their own API key in the sidebar when using the app.

**How it works:**
- Each user enters their own API key in the sidebar
- Keys are stored in session only (temporary, lost on page reload)
- Each user only pays for their own usage
- This is the ONLY way end users can use AI-powered analytics

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

### API Key Not Loading (For Owner/Developer Testing)

If you've configured secrets.toml but your key isn't loading when YOU test the app:

1. Make sure the file is named exactly `secrets.toml` (not `secrets.toml.txt`)
2. Check that it's in the `.streamlit` directory
3. Verify the format matches the example
4. Restart the Streamlit app

**Note**: End users should NOT expect automatic API key loading - they must enter their own keys manually.

### Still Having Issues?

Open an issue on [GitHub](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/issues)
