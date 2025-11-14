# Web Apps Comparison

ChatConvert-Toolkit includes **two web interfaces** for different use cases.

## 🎨 Streamlit App (Recommended)

**File:** `app_streamlit.py` (root folder)

**Purpose:** Full-featured web UI for end users

**Features:**
- Beautiful gradient-styled interface
- Interactive file upload/download
- Real-time conversion with progress
- Analytics with interactive charts
- Three tabs: Convert, Analytics, About
- Drag & drop support
- Download buttons with proper MIME types

**Best For:**
- Public-facing web app
- Non-technical users
- Visual analytics
- Quick demos
- Personal use

**Deploy To:**
- ✅ **Streamlit Cloud** (FREE)
- Heroku
- DigitalOcean
- Any Python hosting

**Run Locally:**
```bash
streamlit run app_streamlit.py
# Opens at http://localhost:8501
```

**Deploy to Streamlit Cloud:**
1. Fork repository
2. Visit https://share.streamlit.io/deploy
3. Connect GitHub
4. Set main file: `app_streamlit.py`
5. Deploy!

---

## 🔌 Flask REST API (Optional)

**File:** `chatconvert/web/app.py` (subfolder)

**Purpose:** REST API for programmatic access

**Features:**
- RESTful endpoints (JSON responses only)
- CORS enabled
- File upload/download via API
- Three endpoints:
  - `GET /api/formats` - List formats
  - `POST /api/convert` - Convert file
  - `POST /api/analyze` - Analyze file
- Minimal HTML template (embedded)

**Best For:**
- Integrating with other apps
- Mobile app backends
- Custom frontends
- Automation scripts
- Microservices

**Deploy To:**
- Render
- Railway
- PythonAnywhere
- Heroku
- DigitalOcean App Platform

**Run Locally:**
```bash
python -m chatconvert.web.app
# Opens at http://localhost:5000
```

**API Usage:**
```bash
# List formats
curl http://localhost:5000/api/formats

# Convert file
curl -X POST -F "file=@chat.csv" -F "format=html" \
  http://localhost:5000/api/convert --output result.html

# Analyze file
curl -X POST -F "file=@chat.csv" \
  http://localhost:5000/api/analyze
```

---

## 📊 Quick Comparison

| Feature | Streamlit App | Flask API |
|---------|---------------|-----------|
| **UI** | ✅ Beautiful web interface | ⚠️ Basic HTML (API-focused) |
| **File Upload** | ✅ Drag & drop | ✅ Multipart form |
| **Charts** | ✅ Interactive analytics | ❌ JSON only |
| **Ease of Use** | ✅ Point and click | ⚠️ Requires API knowledge |
| **Deployment** | ✅ Streamlit Cloud (FREE) | ⚠️ Requires Python hosting |
| **For End Users** | ✅ Perfect | ❌ Not ideal |
| **For Developers** | ✅ Good | ✅ Perfect |
| **Mobile Friendly** | ✅ Yes | ⚠️ API only |

---

## 🎯 Recommendation

### For Your Use Case (Streamlit Cloud)

**Use:** `app_streamlit.py`

**Why:**
- Beautiful UI out of the box
- Free deployment to Streamlit Cloud
- No server management needed
- Perfect for sharing with others
- Analytics with charts included

### When to Use Flask API

Use `chatconvert/web/app.py` if you need to:
- Build a custom React/Vue/Angular frontend
- Integrate with mobile apps
- Create automation scripts
- Run as a microservice
- Build on a different platform (not Streamlit)

---

## 🚀 Deployment Commands

### Streamlit Cloud (Recommended)
```bash
# No commands needed!
# Just:
# 1. Fork repo
# 2. Go to share.streamlit.io/deploy
# 3. Select: app_streamlit.py
# 4. Deploy!
```

### Flask (Alternative)
```bash
# Render
# Add to render.yaml:
# services:
#   - type: web
#     runtime: python
#     buildCommand: pip install -r requirements.txt
#     startCommand: python -m chatconvert.web.app

# Or Heroku
# Add to Procfile:
# web: python -m chatconvert.web.app
```

---

## 🤝 Can They Run Together?

**Yes!** You can run both simultaneously:

```bash
# Terminal 1: Streamlit UI for users
streamlit run app_streamlit.py
# → http://localhost:8501

# Terminal 2: Flask API for developers
python -m chatconvert.web.app
# → http://localhost:5000
```

This gives you:
- Web UI for end users (port 8501)
- REST API for automation (port 5000)

---

## 📝 Summary

**For Streamlit Cloud deployment:**
- ✅ Use `app_streamlit.py`
- Set as main file in Streamlit Cloud
- Get beautiful UI + FREE hosting

**For REST API needs:**
- Use `chatconvert/web/app.py`
- Deploy to Render/Railway/etc.
- Integrate with custom apps

**Most users should use Streamlit!** 🎨
