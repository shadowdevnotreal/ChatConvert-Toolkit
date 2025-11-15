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

### 🚨 IMPORTANT: How API Keys Work

**This app is designed so each user must enter their own API key!**

- 🔒 **By Design**: The app code does NOT read from Streamlit secrets
- ✅ **Everyone (including owner)**: Must enter their own API key in the sidebar
- 💰 **Why?**: Each person pays for their own usage - no shared costs
- 🔄 **Session-based**: Keys are stored temporarily and cleared on page reload

### For Local Development (Optional Convenience)

If running the app locally on your computer, you can save your key to avoid re-entering it:

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
   Your key will be available when running locally.

⚠️ **IMPORTANT**: This ONLY works for local development. The deployed app does NOT use secrets.

### For Deployed Apps (Streamlit Cloud, etc.)

**Everyone must enter their own API key manually in the sidebar.**

- No automatic key loading from secrets
- Each visitor provides their own key
- Keys are session-based (lost on page reload)
- This prevents sharing API costs across users

**How to use:**
1. Visit the app
2. Enter your API key in the sidebar
3. Click "🧪 Test" to validate it
4. Use AI-powered analytics

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

### API Key Not Loading (Local Development Only)

If you've configured secrets.toml for local development but your key isn't loading:

1. Make sure the file is named exactly `secrets.toml` (not `secrets.toml.txt`)
2. Check that it's in the `.streamlit` directory
3. Verify the format matches the example
4. Restart the Streamlit app

**Note**: secrets.toml ONLY works when running locally. Deployed apps require manual key entry.

### Still Having Issues?

Open an issue on [GitHub](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/issues)
