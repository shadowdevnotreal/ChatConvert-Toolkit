#!/usr/bin/env python3
"""
Example: How to let users provide their own Groq API key in Streamlit.

Add this to app_streamlit.py to allow optional AI analytics.
"""

import streamlit as st
from chatconvert.analytics import AnalyticsEngine

# Add this in the sidebar or analytics tab:

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🤖 AI Analytics (Optional)")

    # Let user input their own API key
    user_api_key = st.text_input(
        "Groq API Key (optional)",
        type="password",
        help="Add your Groq API key for AI-powered sentiment/topic analysis. Leave empty for keyword-based analytics."
    )

    if user_api_key:
        st.success("✓ AI analytics enabled")
    else:
        st.info("Using keyword-based analytics (no API key needed)")

# Then when initializing analytics:

# Check for API key in secrets (your key) OR user input (their key)
api_key = st.secrets.get("GROQ_API_KEY", user_api_key if user_api_key else None)
use_ai = api_key is not None

analytics_engine = AnalyticsEngine(use_ai=use_ai, api_key=api_key)

# This gives you:
# - Free keyword-based analytics by default
# - AI analytics if YOU add your key to secrets
# - AI analytics if USERS add their own key
