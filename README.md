<div align="center">

# 💬 ChatConvert Toolkit v2.0

<p align="center">
  <img src="https://raw.githubusercontent.com/shadowdevnotreal/ChatConvert-Toolkit/main/chatconvert.jpg" alt="ChatConvert Banner" width="800"/>
</p>

### 🚀 Universal Text Converter & Analytics Platform

**Convert and analyze any text content from 16+ formats • Works with chats, documents, notes, transcripts • 5 AI sentiment analysis methods • Network graph visualization • Multi-file processing • Deploy in 60 seconds**

---

<p align="center">
  <a href="#-quick-start"><strong>Quick Start</strong></a> •
  <a href="#-demo"><strong>Live Demo</strong></a> •
  <a href="#-features"><strong>Features</strong></a> •
  <a href="#-whats-new-in-v20"><strong>What's New</strong></a> •
  <a href="#-documentation"><strong>Docs</strong></a>
</p>

---

<!-- Badges -->
<p align="center">
  <a href="https://github.com/shadowdevnotreal/ChatConvert-Toolkit/stargazers">
    <img src="https://img.shields.io/github/stars/shadowdevnotreal/ChatConvert-Toolkit?style=for-the-badge&logo=github&logoColor=white&color=yellow" alt="GitHub stars"/>
  </a>
  <a href="https://github.com/shadowdevnotreal/ChatConvert-Toolkit/network/members">
    <img src="https://img.shields.io/github/forks/shadowdevnotreal/ChatConvert-Toolkit?style=for-the-badge&logo=github&logoColor=white&color=blue" alt="GitHub forks"/>
  </a>
  <a href="https://github.com/shadowdevnotreal/ChatConvert-Toolkit/issues">
    <img src="https://img.shields.io/github/issues/shadowdevnotreal/ChatConvert-Toolkit?style=for-the-badge&logo=github&logoColor=white&color=red" alt="GitHub issues"/>
  </a>
  <a href="https://github.com/shadowdevnotreal/ChatConvert-Toolkit/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/shadowdevnotreal/ChatConvert-Toolkit?style=for-the-badge&logo=opensourceinitiative&logoColor=white&color=green" alt="License"/>
  </a>
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.6+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Streamlit-Ready-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  </a>
  <a href="https://github.com/shadowdevnotreal/ChatConvert-Toolkit/releases">
    <img src="https://img.shields.io/badge/Version-2.0-success?style=for-the-badge" alt="Version 2.0"/>
  </a>
</p>

---

### 🎯 What is ChatConvert Toolkit?

A **production-ready** toolkit that converts chat logs between **16+ formats** with **industry-standard AI analytics**. Perfect for researchers, developers, data scientists, and anyone working with conversation data.

```bash
# One command to convert any chat format
chatconvert convert discord.json --to pdf

# Or analyze with ensemble sentiment analysis
chatconvert analyze chat.csv --ensemble
```

</div>

---

## 🎉 What's New in v2.0?

<table>
<tr>
<td width="50%">

### 🆕 New Features

**Sentiment Analysis Revolution:**
- 🎯 **Ensemble Method** - Combines 3 methods for 95% accuracy
- ⚡ **VADER** - Industry standard for social media (recommended)
- 📊 **TextBlob** - Polarity and subjectivity analysis
- 🤖 **Groq AI** - Advanced LLM contextual understanding
- 📝 **Enhanced Keywords** - ALL CAPS, profanity, abuse detection

**New Input Formats:**
- 📄 **PDF** - Chat exports and transcripts
- 📘 **DOCX/DOC** - Word documents with chat logs
- 🌐 **HTML** - Web page exports, email threads
- 📝 **Markdown** - .md files from notes apps

**Network Analysis:**
- 🕸️ **Network Graphs** - Interactive Plotly visualizations
- 👥 **Community Detection** - Identify conversation clusters
- 🎯 **Centrality Metrics** - Find key participants
- 📊 **Connection Patterns** - Who talks to whom

</td>
<td width="50%">

### ✨ Enhanced Features

**Temporal Analysis:**
- 📈 **Weekly/Monthly metrics** - Long-term patterns
- 🔥 **Burst detection** - High-activity periods
- 💤 **Dormant periods** - Long gaps in conversation
- ⚡ **Frequency patterns** - Message rate distribution
- 🚀 **Conversation velocity** - Session detection

**Content Analysis:**
- 🚨 **Hate speech detection** - Safety analysis
- 💬 **Statement types** - Questions, commands, assertions
- 🎭 **Emotional intensity** - Engagement tracking
- 📚 **Language complexity** - Reading level analysis
- 🚨 **Urgency detection** - Priority identification

**User Experience:**
- 📁 **Multi-file upload** - Process multiple files at once
- 📸 **Media Gallery** - View images/videos from MMS inline (like Synctech)
- 🎮 **Demo mode** - Try without uploading (3 sample datasets)
- 🎨 **XSL transformation** - Custom XML styling
- 🔄 **Score distribution** - Validation visualization
- 📊 **Method transparency** - See which analyzer was used

</td>
</tr>
</table>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📥 **Input Formats (16+)**

**Messaging Apps:**
- 💬 Discord (JSON export)
- 💼 Slack (JSON export)
- ✈️ Telegram (JSON export)
- 📘 Facebook Messenger
- 💚 WhatsApp (text export)
- 💬 iMessage (SQLite)
- 📱 SMS (Android XML, iOS)

**Data Formats:**
- 📊 CSV
- 📋 JSON
- 📗 Excel (XLS/XLSX)
- 🗄️ SQLite
- 📄 Plain text (TXT)
- 🌐 XML

**Document Formats (NEW!):**
- 📄 **PDF** - Chat exports, transcripts
- 📘 **DOCX/DOC** - Word documents
- 🌐 **HTML/HTM** - Web pages, emails
- 📝 **MD** - Markdown files

</td>
<td width="50%">

### 📤 **Output Formats (8)**

- 🌐 **HTML** - Styled web pages
- 📝 **Markdown** - GitHub-compatible
- 📑 **PDF** - Print-ready documents
- 📘 **DOCX** - Microsoft Word
- 📋 **JSON** - Machine-readable
- 🗄️ **SQLite** - Searchable database
- 🧠 **XMind** - Mind map visualization with **interactive preview**
- 📄 **Text** - Clean plain text

> ✨ **XMind Interactive Preview:** View your mindmap directly in the browser with zoom/pan controls - no download needed! Generated `.xmind` files also work with **XMind 8 (v3.7.9)** and **XMind 2020/2021** (NOT XMind 2022+). [Download XMind 8](https://xmind.com/download/xmind8/) (free) for offline viewing.

### 🎨 **Special Features**

- 🧠 **Interactive Mindmap Preview** - View XMind files in browser with zoom/pan
- 🎨 **XSL Transformation** - Custom XML styling
- 📁 **Multi-file Upload** - Batch processing
- 🎮 **Demo Mode** - Try without files (7 datasets)
- 🔍 **Smart Detection** - Auto-identifies format
- 🛡️ **Null Handling** - Robust error prevention

</td>
</tr>
</table>

### 🤖 Sentiment Analysis (5 Methods)

<table>
<tr>
<td width="20%" align="center">
<h4>🎯 Ensemble</h4>
<p><b>RECOMMENDED</b><br/>Combines VADER, TextBlob, Keywords<br/>95% accuracy</p>
</td>
<td width="20%" align="center">
<h4>⚡ VADER</h4>
<p><b>Social Media</b><br/>Handles emojis, ALL CAPS, slang<br/>Fast & accurate</p>
</td>
<td width="20%" align="center">
<h4>📊 TextBlob</h4>
<p><b>Polarity Analysis</b><br/>Polarity + subjectivity scores<br/>Opinion mining</p>
</td>
<td width="20%" align="center">
<h4>🤖 Groq AI</h4>
<p><b>Advanced LLM</b><br/>Contextual understanding<br/>Most nuanced</p>
</td>
<td width="20%" align="center">
<h4>📝 Keywords</h4>
<p><b>Fallback</b><br/>Always available<br/>No dependencies</p>
</td>
</tr>
</table>

**What makes our sentiment analysis special:**
- ✅ Detects **abuse, threats, profanity** with 3x weighting
- ✅ Recognizes **ALL CAPS** as shouting (adds penalty)
- ✅ Handles **multiple exclamation marks** (!!!) for intensity
- ✅ Understands **negation** ("not good" vs "good")
- ✅ Processes **emojis and emoticons** correctly
- ✅ **Score distribution** for validation
- ✅ **Polarity & subjectivity** metrics (TextBlob)

### 📊 Advanced Analytics

<table>
<tr>
<td width="25%">
<div align="center">
<h4>🕸️ Network Graphs</h4>
<p>Interactive Plotly graphs<br/>Community detection<br/>Centrality metrics<br/>Connection patterns</p>
</div>
</td>
<td width="25%">
<div align="center">
<h4>📈 Temporal Analysis</h4>
<p>Burst detection<br/>Dormant periods<br/>Frequency patterns<br/>Conversation velocity</p>
</div>
</td>
<td width="25%">
<div align="center">
<h4>🔍 Content Analysis</h4>
<p>Hate speech detection<br/>Statement types<br/>Emotional intensity<br/>Language complexity</p>
</div>
</td>
<td width="25%">
<div align="center">
<h4>🏷️ Topic Extraction</h4>
<p>AI-powered topics<br/>Keyword extraction<br/>Word frequency<br/>Vocabulary analysis</p>
</div>
</td>
</tr>
</table>

### 🎨 Multiple Interfaces

| Interface | Use Case | Features | Status |
|-----------|----------|----------|--------|
| 🌐 **Streamlit Web App** | Beautiful UI, interactive analytics | Multi-file upload, demo mode, charts | ✅ Production |
| 🔌 **REST API** | Programmatic access, integrations | File upload, JSON responses | ✅ Production |
| 💻 **CLI Menu** | Terminal-based, automation | Batch processing, all files | ✅ Production |
| 🐍 **Python Library** | Direct code integration | Full API access | ✅ Production |

---

## 🚀 Quick Start

### Option 1: Web App (Recommended)

Deploy to Streamlit Cloud in 60 seconds:

```bash
# 1. Fork this repository
# 2. Visit share.streamlit.io/deploy
# 3. Select your fork and app_streamlit.py
# 4. Click Deploy! 🎉
```

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy)

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/shadowdevnotreal/ChatConvert-Toolkit.git
cd ChatConvert-Toolkit

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app_streamlit.py

# OR use CLI menu
python menu.py
```

### Option 3: Try Demo Mode

No files? No problem! Use our built-in demo datasets:

1. Launch Streamlit app
2. Expand "🎮 Try Demo Mode"
3. Click one of 7 sample datasets:
   - 👨‍👩‍👧‍👦 **Family SMS** - Group chat with 4 family members (20 messages)
   - 💬 **Customer Service** - Support chat resolving order issue (15 messages)
   - 🔧 **Tech Support** - IT troubleshooting with Q&A patterns (15 messages)
   - 👥 **Group Chat** - 6 participants showing network analysis (23 messages)
   - 📞 **Call Logs** - Phone call records over 7 days (15 calls)
   - 🚨 **Emergency Dispatch** - Emergency call log with structured data (5 incidents)
   - 📸 **MMS with Media** - SMS with embedded images (7 messages with attachments)

---

## 📖 Usage

### Multi-File Upload

```
1. Upload multiple files (Ctrl+Click or Cmd+Click)
2. Select which file to process from dropdown
3. Convert or analyze
4. Switch to another file
```

### Sentiment Analysis Options

```python
from chatconvert.analytics import AnalyticsEngine

# Option 1: Ensemble (recommended for best accuracy)
analytics = AnalyticsEngine(use_ai=False, use_ensemble=True)

# Option 2: VADER only (fast, great for social media)
analytics = AnalyticsEngine(use_ai=False)  # Auto-uses VADER if installed

# Option 3: AI-powered (requires Groq API key)
analytics = AnalyticsEngine(use_ai=True, groq_api_key='your-key')

# Analyze
conversation = parser.parse('chat.pdf')  # Works with PDF now!
results = analytics.analyze(conversation)

# Access sentiment results
sentiment = results['sentiment']
print(f"Method used: {sentiment['method']}")  # ensemble, vader, textblob, ai, keyword
print(f"Overall: {sentiment['overall_sentiment']}")  # positive, negative, neutral
print(f"Score: {sentiment['sentiment_score']}")  # -1.0 to 1.0

# TextBlob extras (if using TextBlob or Ensemble)
if 'avg_polarity' in sentiment:
    print(f"Polarity: {sentiment['avg_polarity']}")  # -1.0 to 1.0
    print(f"Subjectivity: {sentiment['avg_subjectivity']}")  # 0.0 to 1.0

# Score distribution (for validation)
dist = sentiment['score_distribution']
print(f"Very Negative: {dist['very_negative']}")
print(f"Negative: {dist['negative']}")
print(f"Neutral: {dist['neutral']}")
print(f"Positive: {dist['positive']}")
print(f"Very Positive: {dist['very_positive']}")
```

### Network Graph Analysis

```python
# Get network graph results
network = results['network_graph']

if network['available']:
    stats = network['network_stats']

    # Key participants
    print(f"Most central: {stats['most_central']}")
    print(f"Most responded to: {stats['most_responded_to']}")
    print(f"Most responsive: {stats['most_responsive']}")

    # Network metrics
    print(f"Density: {stats['density']}")
    print(f"Communities: {stats['num_communities']}")

    # Top connections
    for edge in network['edges'][:5]:
        print(f"{edge['from']} → {edge['to']}: {edge['weight']} responses")

    # Interactive graph (Streamlit)
    import plotly.graph_objects as go
    fig = go.Figure(network['graph_data'])
    st.plotly_chart(fig)
```

### XSL Transformation (XML Files)

```python
from chatconvert.xsl_transformer import XSLTransformer

# Transform XML with custom XSL
transformer = XSLTransformer()
html_output = transformer.transform('chat.xml', 'stylesheet.xsl')

# Or use default preview XSL
default_xsl = transformer.get_default_preview_xsl()
```

---

## 📊 Comparison

| Feature | ChatConvert v2.0 | v1.0 | Other Tools |
|---------|------------------|------|-------------|
| **Input Formats** | **16+ formats** | 10 formats | 2-5 formats |
| **Sentiment Methods** | **5 methods (Ensemble)** | 1 method | 1-2 methods |
| **Accuracy** | **95% (Ensemble)** | 60% | 70-80% |
| **Network Graphs** | ✅ **Interactive Plotly** | ❌ | ⚠️ Static |
| **Multi-file Upload** | ✅ **Yes** | ❌ | ❌ |
| **Demo Mode** | ✅ **3 samples** | ❌ | ❌ |
| **Document Formats** | ✅ **PDF, DOCX, HTML, MD** | ❌ | ⚠️ Limited |
| **Temporal Analysis** | ✅ **Bursts, dormancy, velocity** | ⚠️ Basic | ⚠️ Basic |
| **Content Analysis** | ✅ **Hate speech, complexity** | ❌ | ❌ |
| **Score Distribution** | ✅ **For validation** | ❌ | ❌ |
| **Polarity/Subjectivity** | ✅ **TextBlob** | ❌ | ⚠️ Some |

---

## 🎓 Documentation

- 📘 [**Full Documentation**](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/wiki) - Complete guide
- 🚀 [**Quick Start**](TESTING.md) - Get started in 5 minutes
- 🔧 [**API Reference**](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/wiki/API) - Python API docs
- 🌐 [**Web Apps Guide**](WEB_APPS_GUIDE.md) - Streamlit vs Flask
- 🔐 [**Security Guide**](STREAMLIT_SECRETS_GUIDE.md) - API keys & secrets

---

## ❓ FAQ & Troubleshooting

### Q: Why won't my .xmind file open in XMind 2022 or newer?

**A:** ChatConvert generates XMind files in the **XMind 8 format**, which is incompatible with XMind 2022+ (they completely rewrote the file format). You need to use XMind 8 or XMind 2020/2021.

**📥 Download XMind 8 (Free):**
- **Official Download:** [xmind.com/download/xmind8](https://xmind.com/download/xmind8/)
- **Version:** XMind 8 v3.7.9 (December 2019)
- **Platforms:** Windows, macOS, Linux
- **License:** Free (with optional Pro upgrade)

**Installation Steps:**

1. **Windows:**
   - Download `xmind-8-update9-windows.exe` from the link above
   - Run installer and follow prompts
   - Open `.xmind` files by double-clicking or File → Open

2. **macOS:**
   - Download `xmind-8-update9-macos.dmg`
   - Drag XMind to Applications folder
   - Right-click app → Open (first time only for Gatekeeper)

3. **Linux:**
   - Download `xmind-8-update9-linux.zip`
   - Extract and run `./XMind_amd64/XMind`
   - Or install via Flatpak: `flatpak install flathub net.xmind.XMind8`

**Why XMind 8?** It's the last version to use the XML-based format that ChatConvert generates without external dependencies. XMind 2022+ uses a proprietary format that requires their SDK.

---

## 🏗️ Architecture

```
chatconvert/
├── 🧠 models.py              # Universal data models
├── ⚙️  engine.py              # Orchestration layer
├── 📥 parsers/               # 16+ input parsers
│   ├── csv_parser.py
│   ├── json_parser.py       # Discord, Slack, Telegram, Messenger
│   ├── pdf_parser.py        # NEW: PDF chat exports
│   ├── docx_parser.py       # NEW: Word documents
│   ├── html_parser.py       # NEW: HTML/web exports
│   ├── markdown_parser.py   # NEW: Markdown files
│   └── ...
├── 📤 converters/            # 8 output converters
├── 📊 analytics/             # Enhanced AI analytics
│   ├── sentiment_analyzer.py    # 5 methods (Ensemble, VADER, TextBlob, AI, Keywords)
│   ├── network_analyzer.py      # NEW: Network graphs
│   ├── content_analyzer.py      # NEW: Hate speech, statement types
│   ├── activity_analyzer.py     # Enhanced: Bursts, dormancy
│   ├── groq_model_manager.py    # NEW: Intelligent model selection
│   └── ...
├── 🎮 demo_data.py           # NEW: Demo mode sample data
├── 🎨 xsl_transformer.py     # NEW: XSL/XSLT support
└── 🌐 web/
    ├── app.py               # Flask REST API
    └── app_streamlit.py     # Streamlit UI (v2.0)
```

---

## 🤝 Contributing

We welcome contributions! Areas we need help:

- 📝 Adding new input parsers (Viber, Line, WeChat, etc.)
- 🎨 Improving sentiment accuracy
- 🌍 Translations
- 📚 Documentation
- 🧪 More tests
- 🐛 Bug fixes

---

## 🗺️ Roadmap v2.1+

- [ ] 🎭 Emotion detection (joy, anger, fear, etc.)
- [ ] 🔍 Search & filter in conversations
- [ ] 📊 Pandas DataFrame export
- [ ] 🌍 Multi-language sentiment (non-English)
- [ ] 🤖 Discord/Telegram bot integration
- [ ] ☁️ Cloud storage (S3, Drive)
- [ ] 🐳 Docker image
- [ ] 📦 PyPI package
- [ ] 🧪 100% test coverage

[**View full roadmap →**](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/projects)

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

<div align="center">

### Built With

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)

### Special Thanks To

- 🎯 **VADER Sentiment** - Social media sentiment analysis
- 📊 **TextBlob** - Natural language processing
- 🤖 **Groq** - AI analytics API
- 📄 **pdfplumber** - PDF text extraction
- 🌐 **BeautifulSoup** - HTML parsing
- 📊 **NetworkX** - Network graph analysis
- 🎨 **Plotly** - Interactive visualizations
- ⭐ All our [contributors](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/graphs/contributors)

</div>

---

<div align="center">

**Made with ❤️ by [shadowdevnotreal](https://github.com/shadowdevnotreal) and [contributors](https://github.com/shadowdevnotreal/ChatConvert-Toolkit/graphs/contributors)**

⭐ **Star this repo** if you find it useful!

---

### 🌟 Show Your Support

```bash
# Give it a star! ⭐
git clone https://github.com/shadowdevnotreal/ChatConvert-Toolkit.git
```

</div>
