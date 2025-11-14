# Streamlit Secrets & API Key Security Guide

## 🔐 How Streamlit Secrets Work

### Your App Deployment

```
YOU deploy app → Add secrets in settings → Your app uses secrets
```

**Security Model:**
```
┌─────────────────────────────────────┐
│  Your Streamlit Cloud Account      │
│  ├── App Settings (Private)         │
│  │   └── Secrets (Encrypted)        │
│  │       └── GROQ_API_KEY = "xyz"   │ ← Only YOUR app sees this
│  └── Public App URL                 │
│      └── Visitors can USE app       │ ← They CANNOT see secrets
└─────────────────────────────────────┘
```

### When Someone Forks Your Repo

```
They fork repo → They deploy THEIR app → They add THEIR OWN secrets
```

**Their deployment is SEPARATE:**
```
┌─────────────────────────────────────┐
│  Their Streamlit Cloud Account     │
│  ├── Their App (Separate)           │
│  │   └── Their Secrets (Empty)      │ ← Your secrets NOT included
│  └── Their Public URL               │
└─────────────────────────────────────┘
```

---

## 🎯 Three Deployment Strategies

### Option 1: No API Key (Free & Open) ⭐ RECOMMENDED

**Setup:**
1. Deploy app as-is
2. Don't add any secrets
3. App uses keyword-based analytics

**Code:**
```python
analytics_engine = AnalyticsEngine(use_ai=False)
```

**Result:**
- ✅ Free for you (no costs)
- ✅ Works for everyone instantly
- ✅ No security concerns
- ✅ Keyword-based analytics (still useful!)

**Best for:**
- Public demos
- Open source projects
- Free services
- Learning/education

---

### Option 2: Your API Key (You Pay)

**Setup:**
1. Deploy app
2. Go to app settings → Secrets
3. Add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

**Modify app_streamlit.py line 75:**
```python
# From:
analytics_engine = AnalyticsEngine(use_ai=False)

# To:
api_key = st.secrets.get("GROQ_API_KEY", None)
analytics_engine = AnalyticsEngine(use_ai=True, api_key=api_key)
```

**Result:**
- ✅ AI-powered analytics for all visitors
- ✅ Better results (sentiment, topics)
- ✅ Your key stays private
- ❌ YOU pay for all usage

**Costs (Groq API):**
- Free tier: ~14,400 requests/day
- After that: ~$0.27 per 1M tokens
- Example: 100 visitors analyzing chats = ~$0.01-0.10/day

**Best for:**
- Personal portfolios
- Low-traffic apps
- When you want to showcase AI features

**Security:**
- ✅ Visitors cannot see your key
- ✅ Key is encrypted in Streamlit
- ✅ Forkers don't get your key

---

### Option 3: User-Provided Keys (Hybrid) 🎯

**Setup:**
Add optional API key input in the UI.

**Modify app_streamlit.py:**

```python
# In sidebar (around line 95):
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🤖 AI Analytics (Optional)")

    user_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Optional: Add your Groq API key for AI-powered analytics"
    )

    if user_api_key:
        st.success("✓ AI analytics enabled")
    else:
        st.info("ℹ️ Using keyword-based analytics")

    st.markdown("[Get free API key](https://console.groq.com)")

# When initializing (line 75):
api_key = st.secrets.get("GROQ_API_KEY", user_api_key if user_api_key else None)
use_ai = api_key is not None
analytics_engine = AnalyticsEngine(use_ai=use_ai, api_key=api_key)
```

**Result:**
- ✅ Free by default (keyword-based)
- ✅ Users can opt-in to AI (their cost)
- ✅ You can still add YOUR key for default AI
- ✅ Best user experience

**Flow:**
1. User visits → keyword analytics (free)
2. User adds key → AI analytics (their cost)
3. OR you add key → AI for everyone (your cost)

**Best for:**
- Public apps with power users
- SaaS-style deployments
- Maximum flexibility

---

## 🔒 Security FAQs

### Q: Can visitors see my API key in secrets?
**A: NO.** Secrets are encrypted and only accessible to your app's server-side code.

### Q: What if someone views my source code on GitHub?
**A: Safe.** The API key is not in your code - it's in Streamlit Cloud settings only.

### Q: What if someone forks my repo and deploys?
**A: Safe.** They get a separate deployment with no access to your secrets.

### Q: Can I share my deployed app publicly?
**A: Yes!** The app URL is public, but secrets remain private.

### Q: What if I accidentally commit my key to Git?
**A: Danger!** Never commit API keys. Use `.gitignore` and secrets only.

---

## 📊 Cost Comparison

### Groq API (Free Tier)
- 14,400 requests/day
- ~30 tokens per message
- ~480,000 tokens/day free
- **Enough for ~500-1000 chat analyses/day**

### Example Scenarios

**Personal Portfolio (10 visitors/day):**
- Free tier: ✅ Plenty
- Cost: $0/month

**Small Demo (100 visitors/day):**
- Free tier: ✅ Sufficient
- Cost: $0/month

**Popular App (1000 visitors/day):**
- Free tier: ⚠️ Might exceed
- Cost: ~$3-10/month

**Viral App (10,000+ visitors/day):**
- Free tier: ❌ Will exceed
- Cost: ~$30-100/month
- **Recommendation:** Use Option 3 (user keys)

---

## 🚀 Recommended Setup

### For This Project (ChatConvert-Toolkit):

**Use Option 1 (No API Key)** for initial deployment:

**Why?**
- ✅ Keyword analytics work great
- ✅ Zero cost for you
- ✅ Works for everyone immediately
- ✅ No usage limits

**Later, if you want AI:**
- Add your key to secrets (Option 2)
- Or add user input (Option 3)

---

## 📝 Step-by-Step: Adding Secrets

### In Streamlit Cloud:

1. **Deploy your app first**
   - Go to share.streamlit.io
   - Connect GitHub repo
   - Deploy `app_streamlit.py`

2. **Add secrets after deployment**
   - Click your app → Settings → Secrets
   - Add in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here_abc123"
   ```
   - Click "Save"
   - Wait ~1 minute for propagation

3. **Verify it works**
   - App will restart automatically
   - Check analytics tab
   - Should see AI-powered results

---

## 🔧 Testing Locally

### With secrets:
```bash
# Create .streamlit/secrets.toml (local only)
mkdir -p .streamlit
echo 'GROQ_API_KEY = "your-key"' > .streamlit/secrets.toml

# Add to .gitignore (IMPORTANT!)
echo ".streamlit/secrets.toml" >> .gitignore

# Run app
streamlit run app_streamlit.py
```

### Without secrets:
```bash
# Just run - will use keyword-based analytics
streamlit run app_streamlit.py
```

---

## ✅ Best Practices

1. **Never commit API keys to Git**
   ```bash
   # Check before committing
   git diff | grep -i "gsk_"
   ```

2. **Use environment variables locally**
   ```bash
   export GROQ_API_KEY="your-key"
   streamlit run app_streamlit.py
   ```

3. **Rotate keys if exposed**
   - If accidentally committed → revoke immediately
   - Generate new key
   - Update in Streamlit secrets

4. **Monitor usage**
   - Check Groq dashboard regularly
   - Set up usage alerts
   - Track costs

5. **Graceful fallback**
   - Always have keyword-based backup
   - Handle API errors gracefully
   - Show clear messages to users

---

## 📖 Summary

**Your Secrets Are Safe:**
- ✅ Only your deployed app sees them
- ✅ Encrypted in Streamlit Cloud
- ✅ Not visible to visitors
- ✅ Not copied to forks

**Recommendation:**
Start with **Option 1** (no API key, free forever), then optionally upgrade to **Option 3** (user-provided keys) if you want AI features.

**Questions?**
- Streamlit Secrets Docs: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- Groq API Docs: https://console.groq.com/docs
