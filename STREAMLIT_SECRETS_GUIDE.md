# API Key Security Guide

## 🔐 How API Keys Work in ChatConvert Toolkit

### Current Implementation (Secure By Design)

**The app does NOT read from Streamlit secrets when deployed.**

This is an intentional security design to prevent:
- Sharing your API key with all visitors
- You paying for everyone else's usage
- Unexpected API costs

```
┌─────────────────────────────────────┐
│  Your Deployed App                 │
│  ├── You visit → Enter your key    │
│  ├── User A visits → Enter their   │
│  ├── User B visits → Enter their   │
│  └── Everyone pays for own usage   │
└─────────────────────────────────────┘
```

---

## 🎯 How to Use the App

### For Deployed Apps (Streamlit Cloud, etc.)

**Everyone must enter their own API key manually:**

1. Visit the app
2. In the sidebar, find "Groq API Key (Optional)"
3. Enter your API key
4. Click "🧪 Test" to validate it
5. Use AI-powered analytics

**Key Features:**
- 🔄 Session-based: Keys are cleared on page reload
- 💰 Fair costs: Each person pays for their own usage
- 🔒 Secure: Your key never leaves your browser session
- ✅ No setup needed: Just enter and go

**Don't have an API key?**
- The app still works great with keyword-based analytics!
- Free forever, no account needed
- Get a free Groq API key at: https://console.groq.com/keys

---

### For Local Development

If you're running the app locally and want to avoid re-entering your key:

1. **Copy the example file:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Add your API key:**
   ```toml
   [default]
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```

3. **Restart the app:**
   ```bash
   streamlit run app_streamlit.py
   ```

⚠️ **IMPORTANT**: This ONLY works when running locally on your computer!

---

## 🔒 Security Model

### What This App Does NOT Do:

❌ Read from Streamlit Cloud secrets
❌ Share owner's API key with visitors
❌ Cause unexpected API costs
❌ Store keys permanently

### What This App DOES:

✅ Requires each user to enter their own key
✅ Stores keys in session only (temporary)
✅ Ensures fair usage costs
✅ Works great without any API key (keyword-based analytics)

---

## 📊 Cost Transparency

### Groq API Free Tier

- **14,400 requests/day**
- **~1,000 chat analyses/day**
- **No credit card required**
- **Free forever**

### Who Pays?

**With this app's design:**
- You analyze your own chats → You pay (free tier)
- Your friend analyzes their chats → They pay (free tier)
- Everyone stays within free limits → $0 cost for everyone

**If app used owner's secrets (NOT how this app works):**
- You analyze → You pay
- Your friend analyzes → YOU pay (shared key)
- 100 visitors analyze → YOU pay for all 100
- Potential for unexpected costs

---

## 🚀 Why This Design?

**Security First:**
- No risk of sharing your API key
- No surprise billing charges
- Each user controls their own usage

**Fair & Transparent:**
- Everyone pays for what they use
- Free tier is generous (1,000 analyses/day)
- No hidden costs

**Better UX:**
- App works instantly without API key (keyword analytics)
- Users opt-in to AI features when they want them
- No configuration required for basic usage

---

## 🔧 For Developers

### Current Code (app_streamlit.py)

```python
# Line ~354: User enters API key in sidebar
user_api_key = st.text_input(
    "Groq API Key (Optional)",
    value=st.session_state.groq_api_key,
    type="password",
    help="Enter your own Groq API key for AI-powered analytics."
)

# Line ~479: Use ONLY session-based API key
api_key = st.session_state.groq_api_key if st.session_state.groq_api_key else None
use_ai = api_key is not None and len(api_key) > 0
analytics_engine = AnalyticsEngine(groq_api_key=api_key, use_ai=use_ai)
```

**Key Points:**
- No `st.secrets.get()` calls for API keys in deployed code
- All keys come from user session state
- Fallback to keyword-based analytics (not secrets)

### Local Development Code

```python
# ONLY reads secrets when running locally
# This code path exists for developer convenience during testing
```

---

## ✅ Best Practices

### For App Users:

1. **Get a free API key**: https://console.groq.com/keys
2. **Enter it in the sidebar** when you want AI features
3. **Don't share your key** with anyone
4. **Monitor your usage** at Groq dashboard

### For Developers/Forkers:

1. **Never commit API keys to Git**
   ```bash
   # Check before committing
   git diff | grep -i "gsk_"
   ```

2. **Use .gitignore for secrets**
   ```bash
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

3. **Test locally with secrets.toml**
   - Create `.streamlit/secrets.toml` for your testing
   - Never commit this file
   - Deployed app won't use it anyway (by design)

4. **Keep the current security model**
   - Don't add `st.secrets` fallbacks for API keys
   - Maintain session-based key storage
   - Let each user provide their own key

---

## 📖 Summary

**This app is designed for security and fairness:**

✅ **Local Development**: Use `secrets.toml` for convenience
✅ **Deployed Apps**: Everyone enters their own API key
✅ **No Shared Costs**: Each person pays for their own usage
✅ **Works Without Keys**: Keyword-based analytics (free forever)

**Questions?**
- Streamlit Docs: https://docs.streamlit.io/
- Groq API Docs: https://console.groq.com/docs
- Report Issues: https://github.com/shadowdevnotreal/ChatConvert-Toolkit/issues
