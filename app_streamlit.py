#!/usr/bin/env python3
"""
ChatConvert Toolkit - Streamlit Web App (Redesigned Single-Page Flow)

Universal chat format converter and analyzer with interactive web interface.
Upload once, do everything - convert, analyze, preview, download.

Version: 2.0.0 - Demo mode fixes applied
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os
from datetime import datetime
import json

# Add chatconvert to path
sys.path.insert(0, str(Path(__file__).parent))

from chatconvert import ConversionEngine
from chatconvert.analytics import AnalyticsEngine

# Page config
st.set_page_config(
    page_title="ChatConvert Toolkit",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsible, but wider when opened
)

# Custom CSS - Make sidebar wider when opened
st.markdown("""
<style>
    /* Sidebar expanded - make it wider for better readability */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 21rem;
    }
    [data-testid="stSidebar"][aria-expanded="true"] > div {
        width: 21rem;
    }

    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .action-button {
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
        margin: 0.5rem;
    }
    .preview-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def preview_content(file_path, format_type):
    """Preview converted content inline - supports ALL formats."""
    try:
        if format_type in ['html']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.markdown("### 🌐 Preview")
            # Show HTML in iframe or as code
            with st.expander("📄 View HTML Source", expanded=False):
                st.code(content[:5000], language='html')
            st.components.v1.html(content, height=600, scrolling=True)

        elif format_type in ['md', 'markdown']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.markdown("### 📝 Preview")
            st.markdown(content)

        elif format_type in ['txt', 'text']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            st.markdown("### 📄 Preview")
            st.text(content[:5000])  # First 5000 chars
            if len(content) > 5000:
                st.info(f"Showing first 5000 characters. Full file: {len(content)} chars")

        elif format_type == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            st.markdown("### 📋 Preview")
            st.json(content)

        elif format_type == 'pdf':
            # PDF preview using base64 embedding
            st.markdown("### 📕 PDF Preview")
            import base64
            with open(file_path, 'rb') as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            st.caption("💡 Tip: If PDF doesn't display, your browser may not support inline PDFs. Use the download button instead.")

        elif format_type in ['docx', 'doc']:
            # DOCX preview by converting to HTML
            st.markdown("### 📘 Document Preview")
            try:
                import mammoth
                with open(file_path, 'rb') as f:
                    result = mammoth.convert_to_html(f)
                    html_content = result.value
                st.components.v1.html(html_content, height=600, scrolling=True)
                if result.messages:
                    with st.expander("⚠️ Conversion Notes", expanded=False):
                        for msg in result.messages:
                            st.text(msg)
            except ImportError:
                # Fallback: extract text using python-docx
                from docx import Document
                doc = Document(file_path)
                text_content = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                st.text_area("Document Text", text_content, height=600)
                st.caption("📝 Displaying plain text extraction. Install 'mammoth' for formatted preview.")

        elif format_type in ['xlsx', 'xls', 'csv']:
            # Excel/CSV preview as dataframe
            st.markdown("### 📊 Data Preview")
            import pandas as pd
            if format_type == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            st.dataframe(df, use_container_width=True, height=600)

            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Size", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        elif format_type == 'xmind':
            # XMind interactive preview with visual mindmap
            st.markdown("### 🧠 Interactive Mind Map Preview")
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                import json

                with zipfile.ZipFile(file_path, 'r') as z:
                    # XMind files contain content.xml
                    if 'content.xml' in z.namelist():
                        xml_content = z.read('content.xml').decode('utf-8')
                        root = ET.fromstring(xml_content)

                        # Parse XMind structure into hierarchical data
                        def parse_topic(topic_elem):
                            """Recursively parse topic and children."""
                            title_elem = topic_elem.find('.//{urn:xmind:xmap:xmlns:content:2.0}title')
                            title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"

                            children_elem = topic_elem.find('.//{urn:xmind:xmap:xmlns:content:2.0}children')
                            children = []
                            if children_elem is not None:
                                for child in children_elem.findall('.//{urn:xmind:xmap:xmlns:content:2.0}topic'):
                                    children.append(parse_topic(child))

                            return {"name": title, "children": children}

                        # Find root topic
                        root_topic = root.find('.//{urn:xmind:xmap:xmlns:content:2.0}topic')
                        if root_topic is not None:
                            mindmap_data = parse_topic(root_topic)

                            # Generate interactive HTML mindmap using D3.js
                            html_mindmap = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <script src="https://d3js.org/d3.v7.min.js"></script>
                                <style>
                                    body {{ margin: 0; font-family: Arial, sans-serif; background: #1a1a2e; }}
                                    .node circle {{ fill: #4a90e2; stroke: #2c5aa0; stroke-width: 2px; }}
                                    .node text {{ font: 12px sans-serif; fill: #ffffff; }}
                                    .link {{ fill: none; stroke: #888; stroke-width: 2px; }}
                                    .node:hover circle {{ fill: #5fa3f5; }}
                                </style>
                            </head>
                            <body>
                                <svg id="mindmap" width="100%" height="600"></svg>
                                <script>
                                    const data = {json.dumps(mindmap_data)};

                                    const width = document.getElementById('mindmap').clientWidth;
                                    const height = 600;

                                    const svg = d3.select("#mindmap");
                                    const g = svg.append("g");

                                    // Create tree layout
                                    const tree = d3.tree().size([height - 100, width - 200]);
                                    const root = d3.hierarchy(data);
                                    tree(root);

                                    // Add zoom behavior
                                    const zoom = d3.zoom()
                                        .scaleExtent([0.5, 3])
                                        .on("zoom", (event) => {{ g.attr("transform", event.transform); }});
                                    svg.call(zoom);

                                    // Center the tree
                                    g.attr("transform", "translate(100,50)");

                                    // Draw links
                                    g.selectAll(".link")
                                        .data(root.links())
                                        .enter().append("path")
                                        .attr("class", "link")
                                        .attr("d", d3.linkHorizontal()
                                            .x(d => d.y)
                                            .y(d => d.x));

                                    // Draw nodes
                                    const node = g.selectAll(".node")
                                        .data(root.descendants())
                                        .enter().append("g")
                                        .attr("class", "node")
                                        .attr("transform", d => `translate(${{d.y}},${{d.x}})`);

                                    node.append("circle")
                                        .attr("r", 6);

                                    node.append("text")
                                        .attr("dy", -10)
                                        .attr("x", d => d.children ? -10 : 10)
                                        .style("text-anchor", d => d.children ? "end" : "start")
                                        .text(d => d.data.name.length > 50 ? d.data.name.substring(0, 47) + "..." : d.data.name);
                                </script>
                            </body>
                            </html>
                            """

                            st.components.v1.html(html_mindmap, height=650, scrolling=False)
                            st.success("✅ Interactive mindmap rendered! Zoom and pan to explore.")
                            st.caption("💡 Tip: Scroll to zoom, click and drag to pan the mindmap")
                        else:
                            st.warning("No root topic found in mind map.")
                    else:
                        st.warning("Could not find content.xml in XMind file.")
                        st.info("Download the file to view in XMind application.")
            except Exception as e:
                st.error(f"Error previewing XMind file: {str(e)}")
                st.info("Download the file to view in XMind application.")

        elif format_type in ['db', 'sqlite', 'sqlite3']:
            # SQLite preview showing tables and sample data
            st.markdown("### 🗄️ Database Preview")
            import sqlite3

            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            if tables:
                st.markdown(f"**Found {len(tables)} table(s):**")

                for table in tables:
                    table_name = table[0]
                    with st.expander(f"📋 Table: {table_name}", expanded=True):
                        # Get row count
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = cursor.fetchone()[0]

                        # Get sample data
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
                        rows = cursor.fetchall()

                        # Get column names
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in cursor.fetchall()]

                        # Display as dataframe
                        import pandas as pd
                        df = pd.DataFrame(rows, columns=columns)
                        st.dataframe(df, use_container_width=True)

                        st.caption(f"Showing {len(rows)} of {row_count} rows")
            else:
                st.warning("No tables found in database.")

            conn.close()

        else:
            st.info(f"📥 {format_type.upper()} preview not yet implemented. Use the download button below.")

    except Exception as e:
        st.warning(f"Could not preview file: {e}")


def main():
    """Main Streamlit application."""

    # Initialize session state
    if 'uploaded_file_data' not in st.session_state:
        st.session_state.uploaded_file_data = None
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None

    # Header
    st.markdown('<h1 class="main-header">💬 ChatConvert Toolkit</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Upload Once • Convert • Analyze • Preview • Download</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Initialize engines
    try:
        conversion_engine = ConversionEngine()
        formats = conversion_engine.list_supported_formats()
    except Exception as e:
        st.error(f"❌ Failed to initialize engines: {e}")
        st.stop()

    # Sidebar with everything
    with st.sidebar:
        st.header("🤖 AI Analytics (Optional)")

        # Initialize session state for API key
        if 'groq_api_key' not in st.session_state:
            st.session_state.groq_api_key = ''
        if 'key_validated' not in st.session_state:
            st.session_state.key_validated = False

        # Check if API key exists in secrets
        secret_key = st.secrets.get("GROQ_API_KEY", None)
        has_secret = secret_key is not None and len(secret_key) > 0

        if has_secret and not st.session_state.groq_api_key:
            st.success("✓ API key loaded from secrets.toml")
            st.caption(f"Key: {secret_key[:8]}...{secret_key[-4:]}")

        # User API key input
        user_api_key = st.text_input(
            "Groq API Key (Optional)" if has_secret else "Groq API Key",
            value=st.session_state.groq_api_key,
            type="password",
            placeholder="gsk_your_api_key_here" if not has_secret else "Using secret key (enter to override)",
            help="Optional: Add your Groq API key for AI-powered analytics. You can also add it to .streamlit/secrets.toml",
            key="api_key_input"
        )

        # Update session state when key changes
        if user_api_key != st.session_state.groq_api_key:
            st.session_state.groq_api_key = user_api_key
            st.session_state.key_validated = False

        # API Key Management Buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🧪 Test", help="Test if API key works", disabled=not user_api_key):
                with st.spinner("Testing key..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=user_api_key)
                        # Simple test API call
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": "Hi"}],
                            max_tokens=5
                        )
                        st.session_state.key_validated = True
                        st.success("✓ Key works!")
                    except Exception as e:
                        st.session_state.key_validated = False
                        st.error(f"❌ Key failed: {str(e)[:50]}")

        with col2:
            if st.button("🗑️ Remove", help="Clear API key", disabled=not user_api_key):
                st.session_state.groq_api_key = ''
                st.session_state.key_validated = False
                st.rerun()

        with col3:
            if user_api_key:
                if st.session_state.key_validated:
                    st.success("✓ Validated", icon="✅")
                else:
                    st.warning("⚠️ Not tested", icon="⚠️")

        # Status display
        if user_api_key or has_secret:
            st.success("✓ AI-powered analytics enabled")
            if has_secret and not user_api_key:
                st.caption("Using API key from secrets.toml")
            else:
                st.caption("Using AI for better sentiment and topic detection")
        else:
            st.info("ℹ️ Using keyword-based analytics")
            st.caption("Free forever, no API key needed")

        with st.expander("📖 How to get & configure API key"):
            st.markdown("""
            **Get your free Groq API key:**

            1. Visit [console.groq.com](https://console.groq.com)
            2. Sign up (free account)
            3. Go to API Keys section
            4. Click "Create API Key"
            5. Copy the key

            **Option 1: Use secrets.toml (recommended)**
            ```bash
            # Copy example file
            cp .streamlit/secrets.toml.example .streamlit/secrets.toml

            # Edit and add your key
            nano .streamlit/secrets.toml
            ```
            Then restart the app - your key will load automatically!

            **Option 2: Enter manually**
            Paste your key in the input field above (temporary, lost on reload)

            **Free tier includes:**
            - 14,400 requests/day
            - ~1000 chat analyses/day
            - No credit card required

            **Why add an API key?**
            - Better sentiment analysis
            - More accurate topic extraction
            - AI-powered insights
            """)

        st.markdown("---")
        st.markdown("### 📋 Supported Formats")

        with st.expander("📥 Input Formats (16+)", expanded=False):
            st.markdown("**💬 Messaging Apps**")
            st.markdown("• Discord • Slack • Telegram  \n• Messenger • WhatsApp  \n• iMessage • SMS")

            st.markdown("**📊 Data Formats**")
            st.markdown("• CSV • JSON • Excel (XLSX/XLS)  \n• SQLite • XML • TXT")

            st.markdown("**📄 Documents**")
            st.markdown("• PDF • DOCX/DOC  \n• HTML/HTM • Markdown")

        with st.expander("📤 Output Formats (8)", expanded=False):
            st.markdown("""
            • 🌐 **HTML** - Interactive web page
            • 📝 **Markdown** - Universal text format
            • 📑 **PDF** - Shareable document
            • 📘 **DOCX** - Microsoft Word
            • 📋 **JSON** - Structured data
            • 🗄️ **SQLite** - Database format
            • 🧠 **XMind** - Mind map visualization
            • 📄 **TXT** - Plain text export
            """)

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        Upload any text content once, then:
        - Convert to any format
        - Analyze with AI/keywords
        - Preview results inline
        - Download output files

        Works with chats, documents, notes, transcripts, and more!
        """)

    # Initialize analytics engine
    try:
        # Prefer session state key, fall back to secrets
        api_key = st.session_state.groq_api_key if st.session_state.groq_api_key else st.secrets.get("GROQ_API_KEY", None)
        use_ai = api_key is not None and len(api_key) > 0
        analytics_engine = AnalyticsEngine(groq_api_key=api_key, use_ai=use_ai)
    except Exception as e:
        st.error(f"❌ Failed to initialize analytics: {e}")
        analytics_engine = AnalyticsEngine(groq_api_key=None, use_ai=False)

    # Main content - Single page flow
    st.header("📤 Upload Your Content")

    # Demo mode section
    with st.expander("🎮 Try Demo Mode - No Upload Required!"):
        st.markdown("""
        **Want to see how ChatConvert works?** Try our 7 demo datasets showcasing different features:
        """)

        # Row 1: Basic conversations
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("👨‍👩‍👧‍👦 Family SMS", use_container_width=True, help="Group chat with 4 family members (20 messages)"):
                st.session_state.demo_mode = 'family'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        with col2:
            if st.button("💬 Customer Service", use_container_width=True, help="Support chat resolving order issue (15 messages)"):
                st.session_state.demo_mode = 'customer_service'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        with col3:
            if st.button("🔧 Tech Support", use_container_width=True, help="IT troubleshooting with Q&A patterns (15 messages)"):
                st.session_state.demo_mode = 'tech_support'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        with col4:
            if st.button("👥 Group Chat", use_container_width=True, help="6 participants - shows network analysis (23 messages)"):
                st.session_state.demo_mode = 'group_chat'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        # Row 2: Advanced features
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📞 Call Logs", use_container_width=True, help="Phone call history over 7 days (15 calls)"):
                st.session_state.demo_mode = 'call_log'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        with col2:
            if st.button("🚨 Emergency Dispatch", use_container_width=True, help="Structured data extraction demo (5 incidents)"):
                st.session_state.demo_mode = 'dispatch'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        with col3:
            if st.button("📸 MMS with Media", use_container_width=True, help="Shows media gallery preview feature (7 messages, 2 images)"):
                st.session_state.demo_mode = 'mms_media'
                st.session_state.uploaded_file_data = None
                st.session_state.uploaded_file_name = None
                st.rerun()

        with col4:
            # Empty column for layout balance
            st.empty()

        if hasattr(st.session_state, 'demo_mode') and st.session_state.demo_mode:
            st.info(f"✅ Demo mode active: **{st.session_state.demo_mode.replace('_', ' ').title()}**")
            if st.button("🔄 Exit Demo Mode"):
                st.session_state.demo_mode = None
                st.rerun()

    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Choose file(s) to convert or analyze",
        type=formats['input'],
        help="16+ formats supported: Messaging apps (Discord, Slack, WhatsApp), Documents (PDF, DOCX, HTML, Markdown), Data (CSV, JSON, Excel, SQLite, XML), Plain text. Works with chats, notes, transcripts, articles - any text content!",
        accept_multiple_files=True,
        key="main_uploader"
    )

    # File selector if multiple files uploaded
    uploaded_file = None
    process_all_files = False
    process_batch = False
    if uploaded_files:
        if len(uploaded_files) > 1:
            st.info(f"📁 **{len(uploaded_files)} files uploaded!**")

            # Add processing mode selector
            st.markdown("**Choose processing mode:**")
            processing_mode = st.radio(
                "Processing mode",
                options=[
                    "📄 Process ONE file at a time",
                    "🔗 Process ALL files TOGETHER (find connections)",
                    "📦 Process ALL files SEPARATELY (batch mode)"
                ],
                index=0,
                label_visibility="collapsed",
                help="One: Select individual file | Together: Merge all into combined analysis | Batch: Process each file separately"
            )

            if "ONE" in processing_mode:
                # Individual file selection
                file_names = [f.name for f in uploaded_files]
                selected_name = st.selectbox(
                    "Select file to process:",
                    file_names,
                    key="file_selector"
                )
                uploaded_file = next(f for f in uploaded_files if f.name == selected_name)

            elif "TOGETHER" in processing_mode:
                process_all_files = True
                uploaded_file = uploaded_files[0]  # Use first file for format detection
                st.success(f"✨ **Multi-file merge mode!** Will analyze {len(uploaded_files)} files together to find connections between parties.")

            else:  # Batch mode
                process_batch = True
                uploaded_file = uploaded_files[0]  # Start with first
                st.success(f"📦 **Batch processing mode!** Will process each of the {len(uploaded_files)} files individually.")
        else:
            uploaded_file = uploaded_files[0]

    # Optional XSL file upload for XML files
    xsl_file = None
    xsl_files = None
    if uploaded_file and uploaded_file.name.lower().endswith('.xml'):
        st.markdown("---")
        st.markdown("#### 🎨 Optional: Upload XSL Stylesheets for XML Preview")
        st.caption("XSL files can have .xsl, .xslt, or .xml extension")
        xsl_files = st.file_uploader(
            "Choose XSL/XSLT file(s) (optional)",
            type=['xsl', 'xslt', 'xml'],
            help="Upload one or more XSL stylesheets (e.g., one for calls, one for SMS). XSL files are XML-based and may have .xml extension.",
            key="xsl_uploader",
            accept_multiple_files=True
        )
        if xsl_files and len(xsl_files) > 0:
            st.info(f"✅ {len(xsl_files)} XSL stylesheet(s) loaded: **{', '.join([f.name for f in xsl_files])}**")

            # Let user select which XSL to use
            if len(xsl_files) == 1:
                xsl_file = xsl_files[0]
                st.caption(f"Using **{xsl_file.name}** for transformation")
            else:
                xsl_names = [f.name for f in xsl_files]
                selected_xsl = st.selectbox(
                    "Select which stylesheet to use for this XML file:",
                    options=xsl_names,
                    help="Choose the appropriate XSL stylesheet for your XML file (e.g., calls.xsl for call logs, sms.xsl for SMS logs)"
                )
                # Find the selected file object
                xsl_file = next((f for f in xsl_files if f.name == selected_xsl), None)
                st.caption(f"Make sure **{xsl_file.name}** is a valid XSLT stylesheet (contains xsl:stylesheet or xsl:transform)")
        else:
            st.caption("No XSL file? We'll use default preview styling.")

    # Handle demo mode or uploaded file
    demo_conversation = None
    if hasattr(st.session_state, 'demo_mode') and st.session_state.demo_mode:
        # Load demo data
        from chatconvert.demo_data import DemoDataGenerator
        try:
            demo_conversation = DemoDataGenerator.get_demo_conversation(st.session_state.demo_mode)
            st.success(f"✅ Demo loaded: **{demo_conversation.title}** ({len(demo_conversation.messages)} messages)")
        except Exception as e:
            st.error(f"Failed to load demo: {e}")
            st.session_state.demo_mode = None

    if uploaded_file:
        # Store in session state
        st.session_state.uploaded_file_data = uploaded_file.getvalue()
        st.session_state.uploaded_file_name = uploaded_file.name
        # Clear demo mode if uploading a file
        st.session_state.demo_mode = None

        st.success(f"✅ File uploaded: **{uploaded_file.name}** ({len(st.session_state.uploaded_file_data):,} bytes)")

    # Process uploaded file or demo data
    if uploaded_file or demo_conversation:
        if uploaded_file:
            st.markdown("---")

            # Show input file preview
            st.header("📋 Preview Input File")
            with st.expander("View uploaded file content", expanded=False):
                try:
                    file_ext = Path(uploaded_file.name).suffix.lstrip('.').lower()
                    # Save to temp for preview
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                        tmp.write(st.session_state.uploaded_file_data)
                        temp_path = tmp.name

                    # Preview based on file type
                    if file_ext == 'xml':
                        # Check if XSL transformation should be applied
                        if xsl_file is not None:
                            try:
                                from chatconvert.xsl_transformer import XSLTransformer

                                st.markdown("**🎨 Styled XML Preview (with XSL transformation)**")

                                # Save XSL to temp file
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.xsl', mode='wb') as tmp_xsl:
                                    tmp_xsl.write(xsl_file.getvalue())
                                    xsl_temp_path = tmp_xsl.name

                                # Apply transformation
                                transformer = XSLTransformer()
                                if transformer.is_available():
                                    try:
                                        html_output = transformer.transform(temp_path, xsl_temp_path)
                                        st.components.v1.html(html_output, height=600, scrolling=True)
                                        st.success("✅ XSL transformation applied successfully!")
                                    except Exception as e:
                                        st.error(f"XSL transformation failed: {e}")
                                        st.caption("Falling back to default XML view...")
                                        # Fallback to default preview
                                        import xml.dom.minidom as minidom
                                        content = st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')
                                        dom = minidom.parseString(content)
                                        pretty_xml = dom.toprettyxml(indent="  ")
                                        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
                                        st.code(pretty_xml[:10000], language='xml')
                                    finally:
                                        # Cleanup XSL temp file
                                        if os.path.exists(xsl_temp_path):
                                            os.unlink(xsl_temp_path)
                                else:
                                    st.warning("⚠️ lxml not installed. Install with: pip install lxml>=4.9.0")
                                    st.caption("Showing default XML preview instead...")
                                    # Show default preview
                                    import xml.dom.minidom as minidom
                                    content = st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')
                                    dom = minidom.parseString(content)
                                    pretty_xml = dom.toprettyxml(indent="  ")
                                    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
                                    st.code(pretty_xml[:10000], language='xml')
                            except Exception as e:
                                st.error(f"Error applying XSL: {e}")
                                st.caption("Showing default XML preview instead...")
                                # Fallback
                                content = st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')[:5000]
                                st.code(content, language='xml')
                        else:
                            # Default XML preview (no XSL)
                            try:
                                import xml.dom.minidom as minidom
                                content = st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')
                                dom = minidom.parseString(content)
                                pretty_xml = dom.toprettyxml(indent="  ")
                                # Remove extra blank lines
                                pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
                                st.code(pretty_xml[:10000], language='xml')  # Show first 10000 chars of formatted XML
                                if len(pretty_xml) > 10000:
                                    st.caption(f"Showing first 10000 characters. Total: {len(pretty_xml)} characters")
                            except:
                                # Fallback to raw XML if parsing fails
                                content = st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')[:5000]
                                st.code(content, language='xml')
                    elif file_ext == 'json':
                        import json
                        try:
                            data = json.loads(st.session_state.uploaded_file_data)
                            st.json(data)
                        except:
                            st.text(st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')[:5000])
                    elif file_ext == 'txt':
                        content = st.session_state.uploaded_file_data.decode('utf-8', errors='ignore')[:5000]
                        st.text(content)
                    elif file_ext in ['csv']:
                        import pandas as pd
                        import io
                        df = pd.read_csv(io.BytesIO(st.session_state.uploaded_file_data))
                        st.dataframe(df.head(100))
                    elif file_ext in ['xlsx', 'xls']:
                        import pandas as pd
                        import io
                        df = pd.read_excel(io.BytesIO(st.session_state.uploaded_file_data))
                        st.dataframe(df.head(100))
                    else:
                        st.info(f"Preview not available for {file_ext} files. Use conversion to see content.")

                    # Cleanup
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    st.warning(f"Could not preview file: {e}")

        st.markdown("---")
        st.header("⚙️ What would you like to do?")

        # Action selector - radio buttons for clear mutually exclusive choice
        action_choice = st.radio(
            "Select action:",
            options=["🔄 Convert", "📊 Analyze", "✨ Both (Convert & Analyze)"],
            index=0,  # Default to Convert
            horizontal=True,
            label_visibility="collapsed"
        )

        # Set action flags based on radio selection
        if action_choice == "🔄 Convert":
            action_convert = True
            action_analyze = False
        elif action_choice == "📊 Analyze":
            action_convert = False
            action_analyze = True
        else:  # Both
            action_convert = True
            action_analyze = True

        # Configuration section
        selected_format = None
        if action_convert:
            st.header("🔄 Conversion Settings")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### Select Output Format")

            with col2:
                # Future feature badge
                st.caption("🔒 Privacy features coming soon!")

            # Format selector
            format_display = [
                ('html', '🌐 HTML (Web page)'),
                ('markdown', '📝 Markdown'),
                ('pdf', '📑 PDF'),
                ('docx', '📘 Word Document'),
                ('json', '📋 JSON'),
                ('txt', '📄 Plain Text'),
                ('sqlite', '🗄️ SQLite Database'),
                ('xmind', '🧠 XMind Map')
            ]

            selected_format = st.selectbox(
                "Output Format",
                options=[fmt for fmt, _ in format_display],
                format_func=lambda x: dict(format_display)[x],
                index=0,
                label_visibility="collapsed"
            )

            # XMind compatibility warning
            if selected_format == 'xmind':
                st.warning("""
                ⚠️ **XMind Compatibility:** Generated `.xmind` files use **XMind 8 format** (2020/2021 compatible).
                They will **NOT** open in XMind 2022+.

                📥 [**Download XMind 8 (free)**](https://xmind.com/download/xmind8/) - Windows, Mac, Linux
                """)

        if action_analyze:
            if not action_convert:
                st.header("📊 Analytics Settings")
            st.info("💡 Analytics will run automatically when you click Process")

        st.markdown("---")

        # Single unified Process button
        if action_convert or action_analyze:
            button_text = "🔄 Convert" if action_convert and not action_analyze else "📊 Analyze" if action_analyze and not action_convert else "✨ Process (Convert & Analyze)"

            if st.button(button_text, type="primary", use_container_width=True, key="process_button"):
                # Process based on selected actions
                conversion_result = None
                analytics_results = None
                input_path = None  # Initialize to None for cleanup safety

                # Conversion
                if action_convert:
                    # Check if we're in demo mode
                    if demo_conversation:
                        # Demo mode - convert directly from Conversation object
                        with st.spinner("Converting demo data..."):
                            try:
                                # Create output file
                                output_filename = f"demo_{st.session_state.demo_mode}.{selected_format}"
                                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{selected_format}') as tmp_output:
                                    output_path = tmp_output.name

                                # Convert directly from Conversation object
                                start_time = datetime.now()
                                converter = conversion_engine.get_converter(selected_format)
                                result = converter.convert(demo_conversation, output_path)
                                duration = (datetime.now() - start_time).total_seconds()

                                if result.success:
                                    # Read output file
                                    with open(output_path, 'rb') as f:
                                        output_data = f.read()

                                    conversion_result = {
                                        'result': result,
                                        'output_data': output_data,
                                        'output_path': output_path,
                                        'output_filename': output_filename,
                                        'duration': duration,
                                        'format': selected_format
                                    }

                                    st.success("✅ **Demo conversion successful!**")

                                    # Show stats
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Messages", result.message_count)
                                    with col2:
                                        st.metric("Size", f"{len(output_data):,} B")
                                    with col3:
                                        st.metric("Duration", f"{duration:.2f}s")
                                    with col4:
                                        st.metric("Format", selected_format.upper())

                                    if result.warnings:
                                        st.warning(f"⚠️ {len(result.warnings)} warnings")

                                else:
                                    st.error("❌ **Conversion failed!**")
                                    if result.errors:
                                        st.markdown("**Errors:**")
                                        for error in result.errors[:5]:
                                            st.markdown(f"• {error}")

                            except Exception as e:
                                st.error(f"❌ Conversion Error: {e}")
                                import traceback
                                with st.expander("Show traceback"):
                                    st.code(traceback.format_exc())
                    else:
                        with st.spinner("Converting..."):
                            try:
                                # Save uploaded file to temp
                                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_input:
                                    tmp_input.write(st.session_state.uploaded_file_data)
                                    input_path = tmp_input.name

                                # Create output file
                                output_filename = Path(uploaded_file.name).stem + f'.{selected_format}'
                                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{selected_format}') as tmp_output:
                                    output_path = tmp_output.name

                                # Convert
                                start_time = datetime.now()
                                result = conversion_engine.convert(input_path, output_path, selected_format)
                                duration = (datetime.now() - start_time).total_seconds()

                                if result.success:
                                    # Read output file
                                    with open(output_path, 'rb') as f:
                                        output_data = f.read()

                                    conversion_result = {
                                        'result': result,
                                        'output_data': output_data,
                                        'output_path': output_path,
                                        'output_filename': output_filename,
                                        'duration': duration,
                                        'format': selected_format
                                    }

                                    st.success("✅ **Conversion successful!**")

                                    # Show stats
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Messages", result.message_count)
                                    with col2:
                                        st.metric("Size", f"{len(output_data):,} B")
                                    with col3:
                                        st.metric("Duration", f"{duration:.2f}s")
                                    with col4:
                                        st.metric("Format", selected_format.upper())

                                    if result.warnings:
                                        st.warning(f"⚠️ {len(result.warnings)} warnings")

                                else:
                                    st.error("❌ **Conversion failed!**")
                                    if result.errors:
                                        st.markdown("**Errors:**")
                                        for error in result.errors[:5]:
                                            st.markdown(f"• {error}")

                                # Cleanup temp input file
                                if input_path and os.path.exists(input_path):
                                    os.unlink(input_path)

                            except Exception as e:
                                st.error(f"❌ Conversion Error: {e}")
                                import traceback
                                with st.expander("Show traceback"):
                                    st.code(traceback.format_exc())
                                # Cleanup on error
                                if input_path and os.path.exists(input_path):
                                    os.unlink(input_path)

                # Analytics
                if action_analyze:
                    st.markdown("---")

                    # Determine spinner text
                    if process_batch:
                        spinner_text = f"Batch processing {len(uploaded_files)} files..."
                    elif process_all_files:
                        spinner_text = "Analyzing multiple files..."
                    else:
                        spinner_text = "Analyzing conversation..."

                    with st.spinner(spinner_text):
                        try:
                            # Batch processing mode - process each file separately
                            if process_batch:
                                st.subheader(f"📦 Batch Processing {len(uploaded_files)} Files")

                                for batch_idx, batch_file in enumerate(uploaded_files, 1):
                                    with st.expander(f"📄 File {batch_idx}/{len(uploaded_files)}: {batch_file.name}", expanded=True):
                                        try:
                                            # Save to temp
                                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(batch_file.name).suffix) as tmp:
                                                tmp.write(batch_file.getvalue())
                                                temp_path = tmp.name

                                            # Parse
                                            parser = conversion_engine._get_parser(temp_path)
                                            batch_conv = parser.parse(temp_path)

                                            # Analyze
                                            batch_results = analytics_engine.analyze(batch_conv)

                                            # Display compact metrics for this file
                                            col1, col2, col3, col4 = st.columns(4)
                                            with col1:
                                                st.metric("Messages", len(batch_conv.messages))
                                            with col2:
                                                st.metric("Participants", len(batch_conv.participants))
                                            with col3:
                                                if 'sentiment' in batch_results:
                                                    sentiment = batch_results['sentiment'].get('overall_sentiment', 'N/A')
                                                    st.metric("Sentiment", sentiment)
                                            with col4:
                                                if 'word_frequency' in batch_results:
                                                    words = batch_results['word_frequency'].get('total_words', 0)
                                                    st.metric("Words", words)

                                            # Media preview for batch files
                                            batch_media = [msg for msg in batch_conv.messages if msg.attachments]
                                            if batch_media:
                                                st.markdown(f"**📸 Media Found:** {len(batch_media)} messages with attachments")
                                                with st.expander("View Media Gallery", expanded=False):
                                                    for idx, msg in enumerate(batch_media[:5], 1):  # Show first 5 for batch
                                                        st.caption(f"Message {idx} - {msg.sender} - {msg.timestamp.strftime('%Y-%m-%d %H:%M')}")
                                                        for att in msg.attachments:
                                                            try:
                                                                data_uri = att.get_data_uri()
                                                                if data_uri:
                                                                    if att.is_image():
                                                                        st.image(data_uri, caption=att.filename, width=300)
                                                                    elif att.is_video():
                                                                        st.video(data_uri)
                                                                    elif att.is_audio():
                                                                        st.audio(data_uri)
                                                            except Exception as e:
                                                                st.warning(f"Could not display {att.filename}")
                                                    if len(batch_media) > 5:
                                                        st.info(f"Showing first 5 messages. Total: {len(batch_media)} with media.")

                                            # Download button for this file's analytics
                                            text_report = analytics_engine.generate_report(batch_conv)
                                            st.download_button(
                                                label=f"📥 Download Report for {batch_file.name}",
                                                data=text_report,
                                                file_name=f"analytics_{batch_file.name}.txt",
                                                mime="text/plain",
                                                key=f"download_batch_{batch_idx}"
                                            )

                                            # Cleanup
                                            try:
                                                os.unlink(temp_path)
                                            except:
                                                pass

                                        except Exception as e:
                                            st.error(f"❌ Failed to process {batch_file.name}: {e}")
                                            import traceback
                                            with st.expander("Show error details"):
                                                st.code(traceback.format_exc())

                                st.success(f"✅ Batch processing complete! Processed {len(uploaded_files)} files.")

                                # Skip the normal analytics flow
                                st.stop()

                            # Get conversation object (non-batch modes)
                            if demo_conversation:
                                # Use demo conversation directly
                                conversation = demo_conversation
                            elif process_all_files:
                                # Multi-file processing: Parse all files and merge
                                from chatconvert.models import Conversation, Participant

                                st.info(f"🔗 Processing {len(uploaded_files)} files to analyze connections...")
                                all_messages = []
                                all_participants_dict = {}
                                temp_files = []

                                for idx, file in enumerate(uploaded_files, 1):
                                    st.caption(f"📄 Parsing file {idx}/{len(uploaded_files)}: {file.name}")

                                    # Save to temp
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp:
                                        tmp.write(file.getvalue())
                                        temp_path = tmp.name
                                        temp_files.append(temp_path)

                                    # Parse
                                    try:
                                        parser = conversion_engine._get_parser(temp_path)
                                        file_conv = parser.parse(temp_path)
                                        all_messages.extend(file_conv.messages)

                                        # Merge participants
                                        for p in file_conv.participants:
                                            if p.username not in all_participants_dict:
                                                all_participants_dict[p.username] = p
                                    except Exception as e:
                                        st.warning(f"⚠️ Could not parse {file.name}: {e}")
                                        continue

                                # Create merged conversation
                                conversation = Conversation(
                                    id="multi_file_analysis",
                                    title=f"Combined Analysis ({len(uploaded_files)} files)",
                                    messages=all_messages,
                                    participants=list(all_participants_dict.values()),
                                    platform="Multi-File Analysis",
                                    conversation_type="merged"
                                )
                                conversation.sort_messages()

                                # Cleanup temp files
                                for tf in temp_files:
                                    try:
                                        os.unlink(tf)
                                    except:
                                        pass

                                st.success(f"✅ Merged {len(all_messages)} messages from {len(uploaded_files)} files!")
                            else:
                                # Single file processing
                                # Save uploaded file to temp and parse
                                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                                    tmp.write(st.session_state.uploaded_file_data)
                                    input_path = tmp.name

                                # Parse conversation
                                parser = conversion_engine._get_parser(input_path)
                                conversation = parser.parse(input_path)

                            # Analyze
                            results = analytics_engine.analyze(conversation)
                            analytics_results = {'conversation': conversation, 'results': results}

                            # Display results
                            st.success("✅ **Analysis complete!**")

                            # Metrics row
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("Total Messages", len(conversation.messages))
                            with col2:
                                st.metric("Participants", len(conversation.participants))
                            with col3:
                                if 'word_frequency' in results and 'error' not in results['word_frequency']:
                                    st.metric("Total Words", results['word_frequency']['total_words'])
                            with col4:
                                if 'word_frequency' in results and 'error' not in results['word_frequency']:
                                    diversity = results['word_frequency']['vocabulary_diversity']
                                    st.metric("Vocabulary", f"{diversity:.2%}")

                            st.markdown("---")

                            # Media Gallery (MMS/SMS with attachments)
                            media_messages = [msg for msg in conversation.messages if msg.attachments]
                            if media_messages:
                                st.subheader("📸 Media Gallery")
                                st.caption(f"Found {len(media_messages)} messages with media attachments")

                                # Count media types
                                total_images = sum(len([att for att in msg.attachments if att.is_image()]) for msg in media_messages)
                                total_videos = sum(len([att for att in msg.attachments if att.is_video()]) for msg in media_messages)
                                total_audio = sum(len([att for att in msg.attachments if att.is_audio()]) for msg in media_messages)

                                # Display media type counts
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("📷 Images", total_images)
                                with col2:
                                    st.metric("🎥 Videos", total_videos)
                                with col3:
                                    st.metric("🎵 Audio", total_audio)

                                st.markdown("---")

                                # Display media in expandable sections by message
                                for idx, msg in enumerate(media_messages[:20], 1):  # Limit to first 20 to avoid performance issues
                                    with st.expander(f"Message {idx} - {msg.sender} - {msg.timestamp.strftime('%Y-%m-%d %H:%M')}", expanded=(idx <= 3)):
                                        # Show message content if available
                                        if msg.content and msg.content != "(MMS - see attachments)":
                                            st.markdown(f"**Message:** {msg.content[:200]}")
                                            st.markdown("---")

                                        # Display attachments
                                        for att in msg.attachments:
                                            try:
                                                data_uri = att.get_data_uri()
                                                if not data_uri:
                                                    st.warning(f"⚠️ {att.filename} - No data available")
                                                    continue

                                                # Display based on type
                                                if att.is_image():
                                                    st.image(data_uri, caption=att.filename, use_container_width=True)
                                                elif att.is_video():
                                                    st.video(data_uri)
                                                    st.caption(f"🎥 {att.filename}")
                                                elif att.is_audio():
                                                    st.audio(data_uri)
                                                    st.caption(f"🎵 {att.filename}")
                                                else:
                                                    st.info(f"📎 {att.filename} ({att.mime_type})")
                                            except Exception as e:
                                                st.error(f"❌ Could not display {att.filename}: {e}")

                                if len(media_messages) > 20:
                                    st.info(f"ℹ️ Showing first 20 messages with media. Total: {len(media_messages)} messages. Download HTML to see all media.")

                                st.markdown("---")

                            # Call Log Analytics (if detected)
                            if 'call_log' in results and 'error' not in results['call_log']:
                                call_data = results['call_log']
                                if call_data.get('is_call_log'):
                                    st.info("📞 **Call Log Detected!** Showing call-specific analytics.")
                                    st.subheader("📞 Call Log Analysis")

                                    # Call metrics
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Total Calls", call_data.get('total_calls', 0))
                                    with col2:
                                        st.metric("Completed", call_data.get('completed_calls', 0))
                                    with col3:
                                        missed = call_data.get('missed_calls', 0)
                                        missed_pct = call_data.get('missed_call_percentage', 0)
                                        st.metric("Missed", f"{missed} ({missed_pct}%)")
                                    with col4:
                                        duration = call_data.get('total_duration_minutes', 0)
                                        st.metric("Total Talk Time", f"{duration}m")

                                    st.markdown("---")

                                    # Call direction
                                    direction = call_data.get('incoming_vs_outgoing', {})
                                    if direction:
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            incoming = direction.get('incoming', 0)
                                            incoming_pct = direction.get('incoming_percentage', 0)
                                            st.metric("📥 Incoming Calls", f"{incoming} ({incoming_pct}%)")
                                        with col2:
                                            outgoing = direction.get('outgoing', 0)
                                            outgoing_pct = direction.get('outgoing_percentage', 0)
                                            st.metric("📤 Outgoing Calls", f"{outgoing} ({outgoing_pct}%)")

                                    st.markdown("---")

                                    # Top contacts
                                    if call_data.get('calls_by_contact'):
                                        st.subheader("👥 Top Contacts")
                                        import pandas as pd
                                        contacts_df = pd.DataFrame(call_data['calls_by_contact'][:10])
                                        if not contacts_df.empty:
                                            # Show as table
                                            st.dataframe(
                                                contacts_df[['contact', 'call_count', 'total_duration_minutes', 'missed_count']],
                                                use_container_width=True,
                                                hide_index=True
                                            )

                                    st.markdown("---")

                                    # Peak calling time
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if call_data.get('peak_calling_time'):
                                            peak = call_data['peak_calling_time']
                                            st.markdown(f"**🕐 Peak Calling Time**")
                                            st.info(f"{peak['time_range']} - {peak['call_count']} calls")

                                    with col2:
                                        if call_data.get('busiest_day'):
                                            busy_day = call_data['busiest_day']
                                            st.markdown(f"**📅 Busiest Day**")
                                            st.info(f"{busy_day['day']} - {busy_day['count']} calls")

                                    # Calls by hour chart
                                    if call_data.get('calls_by_hour'):
                                        st.subheader("📊 Calls by Hour")
                                        import pandas as pd
                                        hourly_df = pd.DataFrame(list(call_data['calls_by_hour'].items()), columns=['hour', 'count'])
                                        if not hourly_df.empty:
                                            st.bar_chart(hourly_df.set_index('hour')['count'])

                                    # Dispatch/Emergency Call Analytics (NEW)
                                    if call_data.get('dispatch_analytics') and call_data['dispatch_analytics'].get('total_dispatch_calls'):
                                        st.markdown("---")
                                        st.subheader("🚨 Emergency Dispatch Analytics")
                                        st.caption("Enhanced information extraction from dispatch logs")

                                        dispatch = call_data['dispatch_analytics']

                                        # Response time metrics
                                        if dispatch.get('average_response_time_minutes'):
                                            col1, col2, col3, col4 = st.columns(4)
                                            with col1:
                                                st.metric("📊 Total Incidents", dispatch.get('total_dispatch_calls', 0))
                                            with col2:
                                                avg_response = dispatch.get('average_response_time_minutes', 0)
                                                st.metric("⏱️ Avg Response", f"{avg_response} min")
                                            with col3:
                                                fastest = dispatch.get('fastest_response_minutes', 0)
                                                st.metric("⚡ Fastest", f"{fastest} min")
                                            with col4:
                                                slowest = dispatch.get('slowest_response_minutes', 0)
                                                st.metric("🐌 Slowest", f"{slowest} min")

                                            st.markdown("---")

                                        # Top locations
                                        if dispatch.get('locations'):
                                            st.subheader("📍 Top Locations")
                                            import pandas as pd
                                            locations_df = pd.DataFrame(
                                                [(loc, count) for loc, count in dispatch['locations'].items()],
                                                columns=['Location', 'Incident Count']
                                            )
                                            st.dataframe(locations_df, use_container_width=True, hide_index=True)

                                        # Event types
                                        if dispatch.get('event_types'):
                                            st.subheader("📋 Event Types")
                                            event_df = pd.DataFrame(
                                                [(event, count) for event, count in dispatch['event_types'].items()],
                                                columns=['Event Type', 'Count']
                                            )
                                            st.dataframe(event_df, use_container_width=True, hide_index=True)

                                        # Call sources
                                        if dispatch.get('call_sources'):
                                            st.subheader("📞 Call Sources")
                                            sources_df = pd.DataFrame(
                                                [(source, count) for source, count in dispatch['call_sources'].items()],
                                                columns=['Source Code', 'Count']
                                            )
                                            st.dataframe(sources_df, use_container_width=True, hide_index=True)

                                    st.markdown("---")

                            # Sentiment
                            if 'sentiment' in results and 'error' not in results['sentiment']:
                                st.subheader("😊 Sentiment Analysis")
                                sentiment = results['sentiment']

                                # Show method used
                                method = sentiment.get('method', 'unknown')
                                method_display = {
                                    'ensemble': '🎯 Ensemble (VADER + TextBlob + Keywords)',
                                    'vader': '⚡ VADER (Social Media Optimized)',
                                    'textblob': '📊 TextBlob (Polarity Analysis)',
                                    'ai': '🤖 Groq AI (Advanced)',
                                    'keyword': '📝 Keyword-based (Basic)'
                                }
                                st.caption(f"Method: {method_display.get(method, method)}")

                                # Main metrics row
                                cols = [1, 1]
                                if 'avg_polarity' in sentiment:
                                    cols.append(1)
                                if 'avg_subjectivity' in sentiment:
                                    cols.append(1)

                                metric_cols = st.columns(cols)

                                with metric_cols[0]:
                                    st.metric("Overall Sentiment", sentiment['overall_sentiment'].upper())
                                    st.caption("Score range: -1.0 to +1.0")

                                with metric_cols[1]:
                                    st.metric("Score", f"{sentiment['sentiment_score']:.2f}")

                                # Show polarity if available (TextBlob/Ensemble)
                                if 'avg_polarity' in sentiment and len(metric_cols) > 2:
                                    with metric_cols[2]:
                                        st.metric("Avg Polarity", f"{sentiment['avg_polarity']:.2f}")
                                        st.caption("TextBlob polarity")

                                # Show subjectivity if available (TextBlob/Ensemble)
                                if 'avg_subjectivity' in sentiment and len(metric_cols) > 3:
                                    with metric_cols[3]:
                                        st.metric("Avg Subjectivity", f"{sentiment['avg_subjectivity']:.2f}")
                                        st.caption("0.0 = objective, 1.0 = subjective")

                                # Distribution chart
                                if 'distribution' in sentiment:
                                    st.markdown("**Message Sentiment Distribution**")
                                    import pandas as pd
                                    dist_data = sentiment['distribution']
                                    st.bar_chart(dist_data)

                                # Score distribution (for validation)
                                if 'score_distribution' in sentiment:
                                    st.markdown("**📊 Sentiment Score Distribution**")
                                    import pandas as pd
                                    score_dist = sentiment['score_distribution']
                                    dist_df = pd.DataFrame.from_dict(score_dist, orient='index', columns=['Count'])
                                    dist_df.index = ['😡 Very Negative', '😞 Negative', '😐 Neutral', '😊 Positive', '🤩 Very Positive']
                                    st.bar_chart(dist_df)

                            st.markdown("---")

                            # Topics
                            if 'topics' in results and 'error' not in results['topics']:
                                st.subheader("🏷️ Main Topics")
                                topics = results['topics']['main_topics'][:10]

                                # Display as pills
                                topics_html = " ".join([f"<span style='background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 1rem; margin: 0.2rem; display: inline-block;'>{topic}</span>" for topic in topics])
                                st.markdown(topics_html, unsafe_allow_html=True)

                            st.markdown("---")

                            # Word Frequency
                            if 'word_frequency' in results and 'error' not in results['word_frequency']:
                                st.subheader("📝 Top Words")
                                words = results['word_frequency']

                                if 'most_common' in words:
                                    import pandas as pd
                                    # Specify column names when creating DataFrame
                                    df = pd.DataFrame(words['most_common'][:20], columns=['word', 'count'])
                                    st.bar_chart(df.set_index('word')['count'])

                            st.markdown("---")

                            # Activity
                            if 'activity' in results and 'error' not in results['activity']:
                                st.subheader("📈 Activity Patterns")
                                activity = results['activity']

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("**📅 Messages per Day (Last 10 days)**")
                                    if 'messages_per_day' in activity:
                                        import pandas as pd
                                        daily = pd.DataFrame(activity['messages_per_day'][:10])
                                        if not daily.empty:
                                            st.bar_chart(daily.set_index('date')['count'])

                                with col2:
                                    st.markdown("**🕐 Messages per Hour**")
                                    if 'messages_per_hour' in activity:
                                        import pandas as pd
                                        hourly = pd.DataFrame(activity['messages_per_hour'])
                                        if not hourly.empty:
                                            st.line_chart(hourly.set_index('hour')['count'])

                                if 'most_active_participant' in activity:
                                    most_active = activity['most_active_participant']
                                    if most_active.get('name'):
                                        st.info(f"🏆 **Most Active:** {most_active['name']} ({most_active['message_count']} messages)")

                            st.markdown("---")

                            # Network Graph Visualization
                            if 'network_graph' in results and results['network_graph'].get('available'):
                                st.subheader("🕸️ Conversation Network")
                                network = results['network_graph']

                                # Display network statistics
                                col1, col2, col3, col4 = st.columns(4)
                                stats = network.get('network_stats', {})

                                with col1:
                                    st.metric("Participants", stats.get('total_nodes', 0))
                                with col2:
                                    st.metric("Connections", stats.get('total_edges', 0))
                                with col3:
                                    density = stats.get('density', 0)
                                    st.metric("Network Density", f"{density:.2%}")
                                with col4:
                                    communities = stats.get('num_communities', 1)
                                    st.metric("Communities", communities)

                                st.markdown("---")

                                # Display interactive graph
                                if 'graph_data' in network:
                                    st.markdown("**Interactive Network Visualization**")
                                    st.caption("Hover over nodes and edges for details. Node size = message count, Edge thickness = response frequency")

                                    import plotly.graph_objects as go
                                    fig = go.Figure(network['graph_data'])
                                    st.plotly_chart(fig, use_container_width=True)

                                st.markdown("---")

                                # Key participants
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    if stats.get('most_central'):
                                        st.markdown("**🎯 Most Central**")
                                        st.info(stats['most_central'])

                                with col2:
                                    if stats.get('most_responded_to'):
                                        st.markdown("**💬 Most Responded To**")
                                        st.info(stats['most_responded_to'])

                                with col3:
                                    if stats.get('most_responsive'):
                                        st.markdown("**↩️ Most Responsive**")
                                        st.info(stats['most_responsive'])

                                st.markdown("---")

                                # Top connections
                                if network.get('edges'):
                                    st.markdown("**🔗 Top Connections**")
                                    st.caption("Strongest response patterns in the conversation")

                                    import pandas as pd
                                    edges = network['edges'][:10]  # Top 10

                                    # Create formatted dataframe
                                    edges_data = []
                                    for edge in edges:
                                        edges_data.append({
                                            'From': edge['from'],
                                            'To': edge['to'],
                                            'Responses': edge['weight'],
                                            'Pattern': f"{edge['from']} → {edge['to']}"
                                        })

                                    edges_df = pd.DataFrame(edges_data)
                                    st.dataframe(edges_df[['Pattern', 'Responses']], use_container_width=True, hide_index=True)

                                # Communities (if multiple detected)
                                if stats.get('num_communities', 1) > 1 and stats.get('communities'):
                                    st.markdown("---")
                                    st.markdown("**👥 Detected Communities**")
                                    st.caption("Groups of people who communicate more with each other")

                                    for i, community in enumerate(stats['communities'], 1):
                                        members = ', '.join(community)
                                        st.markdown(f"**Group {i}:** {members}")

                            # Processing time
                            st.markdown("---")
                            st.info(f"⏱️ Analysis completed in {results.get('processing_time', 0):.2f}s")

                            # Download analytics results
                            st.markdown("---")
                            st.subheader("📥 Download Analytics")

                            # If user converted to a format, offer analytics in same format
                            # Otherwise offer analytics in all formats
                            if action_convert and selected_format:
                                # Download analytics in the same format as conversion
                                try:
                                    # Generate text report
                                    text_report = analytics_engine.generate_report(conversation)

                                    # Create a conversation object for analytics
                                    from chatconvert.models import Conversation, Message, MessageType

                                    # Create analytics message
                                    analytics_message = Message(
                                        id="analytics_1",
                                        sender="Analytics Engine",
                                        content=text_report,
                                        timestamp=datetime.now(),
                                        type=MessageType.TEXT
                                    )

                                    # Create conversation with analytics message
                                    analytics_conv = Conversation(
                                        id=f"{conversation.id}_analytics",
                                        title=f"Analytics Report - {conversation.title}",
                                        messages=[analytics_message],
                                        platform="ChatConvert Analytics",
                                        conversation_type="analytics_report"
                                    )

                                    # Save to temp file and convert
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w') as tmp_analytics:
                                        tmp_analytics.write(text_report)
                                        analytics_input_path = tmp_analytics.name

                                    analytics_output_filename = f"analytics_{conversation.id}.{selected_format}"
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{selected_format}') as tmp_analytics_out:
                                        analytics_output_path = tmp_analytics_out.name

                                    # Convert analytics using the same format as conversion
                                    from chatconvert.converters import CONVERTERS
                                    converter_class = CONVERTERS.get(selected_format)
                                    if converter_class:
                                        converter = converter_class()
                                        converter.convert(analytics_conv, analytics_output_path)
                                    else:
                                        raise ValueError(f"No converter found for format: {selected_format}")

                                    # Read converted analytics
                                    with open(analytics_output_path, 'rb') as f:
                                        analytics_data = f.read()

                                    # Format display name
                                    format_icons = {
                                        'html': '🌐', 'markdown': '📝', 'pdf': '📑',
                                        'docx': '📘', 'json': '📋', 'txt': '📄',
                                        'sqlite': '🗄️', 'xmind': '🧠'
                                    }
                                    icon = format_icons.get(selected_format, '📄')

                                    st.download_button(
                                        label=f"{icon} Download Analytics as {selected_format.upper()}",
                                        data=analytics_data,
                                        file_name=analytics_output_filename,
                                        mime=get_mime_type(selected_format),
                                        help=f"Download analytics report in {selected_format.upper()} format (same as conversion)",
                                        use_container_width=True
                                    )

                                    # Cleanup temp files
                                    if os.path.exists(analytics_input_path):
                                        os.unlink(analytics_input_path)
                                    if os.path.exists(analytics_output_path):
                                        os.unlink(analytics_output_path)

                                except Exception as e:
                                    st.error(f"Failed to generate analytics in {selected_format} format: {e}")
                                    # Fallback to text report
                                    text_report = analytics_engine.generate_report(conversation)
                                    st.download_button(
                                        label="📝 Download Analytics as TXT (fallback)",
                                        data=text_report,
                                        file_name=f"analytics_{conversation.id}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                            else:
                                # If no conversion format selected, offer multiple formats
                                col1, col2, col3, col4 = st.columns(4)

                                with col1:
                                    # Interactive HTML download with charts
                                    def generate_html_report(conv, results_data):
                                        """Generate interactive HTML analytics report with embedded charts"""
                                        import json

                                        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Report - {conv.title}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        h2 {{ color: #764ba2; margin-top: 30px; border-left: 4px solid #764ba2; padding-left: 10px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .metric-label {{ opacity: 0.9; margin-top: 5px; }}
        .chart-container {{ background: #fafafa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .keyword-cloud {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; }}
        .keyword-tag {{ background: #667eea; color: white; padding: 8px 15px; border-radius: 20px; font-size: 14px; }}
        .timestamp {{ color: #999; font-size: 0.9em; }}
        .note {{ background: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196f3; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Interactive Analytics Report</h1>
        <p><strong>Title:</strong> {conv.title}</p>
        <p><strong>Platform:</strong> {conv.platform}</p>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="note">
            💡 <strong>Interactive Report:</strong> This HTML file contains all charts and data. Hover over charts for details, zoom, and pan. Works offline!
        </div>

        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{len(conv.messages)}</div>
                <div class="metric-label">Total Messages</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(conv.participants)}</div>
                <div class="metric-label">Participants</div>
            </div>"""

                                        if 'word_frequency' in results_data:
                                            wf = results_data['word_frequency']
                                            html += f"""
            <div class="metric-card">
                <div class="metric-value">{wf.get('total_words', 0)}</div>
                <div class="metric-label">Total Words</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{wf.get('vocabulary_diversity', 0):.1%}</div>
                <div class="metric-label">Vocabulary</div>
            </div>"""

                                        html += """
        </div>"""

                                        # Sentiment Analysis
                                        if 'sentiment' in results_data and 'error' not in results_data['sentiment']:
                                            sent = results_data['sentiment']
                                            score = sent.get('overall_score', 0)
                                            sentiment_label = sent.get('overall_sentiment', 'NEUTRAL')
                                            # Convert score (-1 to 1) to percentage (0 to 100)
                                            score_pct = ((score + 1) / 2) * 100

                                            html += f"""
        <h2>😊 Sentiment Analysis</h2>
        <p><strong>Overall Sentiment:</strong> <span style="color: {'#f44336' if score < -0.3 else '#ff9800' if score < 0.3 else '#4caf50'}; font-weight: bold;">{sentiment_label}</span></p>
        <p><strong>Score:</strong> {score:.2f} (-1 to +1)</p>
        <div class="sentiment-bar">
            <div class="sentiment-fill" style="width: {score_pct}%;">{score:.2f}</div>
        </div>"""

                                            if 'distribution' in sent:
                                                html += f"""
        <p><strong>Distribution:</strong> {sent['distribution']}</p>"""

                                        # Top Keywords
                                        if 'word_frequency' in results_data and 'top_words' in results_data['word_frequency']:
                                            html += """
        <h2>🔑 Top Keywords</h2>
        <div class="keyword-cloud">"""
                                            for word, count in results_data['word_frequency']['top_words'][:20]:
                                                html += f"""
            <span class="keyword-tag">{word} ({count})</span>"""
                                            html += """
        </div>"""

                                        # Participants Table
                                        if conv.participants:
                                            html += """
        <h2>👥 Participants</h2>
        <table>
            <tr>
                <th>Username</th>
                <th>Messages</th>
            </tr>"""
                                            # Count messages per participant
                                            participant_counts = {}
                                            for msg in conv.messages:
                                                participant_counts[msg.sender] = participant_counts.get(msg.sender, 0) + 1

                                            for participant in sorted(participant_counts.items(), key=lambda x: x[1], reverse=True):
                                                html += f"""
            <tr>
                <td>{participant[0]}</td>
                <td>{participant[1]}</td>
            </tr>"""
                                            html += """
        </table>"""

                                        # Add interactive charts
                                        html += """
        <h2>📈 Interactive Visualizations</h2>"""

                                        # Word Frequency Chart
                                        if 'word_frequency' in results_data and 'top_words' in results_data['word_frequency']:
                                            top_words = results_data['word_frequency']['top_words'][:15]
                                            words = [w[0] for w in top_words]
                                            counts = [w[1] for w in top_words]

                                            html += f"""
        <div class="chart-container">
            <h3>🔤 Top 15 Words Frequency</h3>
            <div id="wordChart"></div>
            <script>
                var wordData = [{{
                    x: {json.dumps(words)},
                    y: {json.dumps(counts)},
                    type: 'bar',
                    marker: {{
                        color: 'rgb(102, 126, 234)',
                        line: {{ color: 'rgb(44, 90, 160)', width: 1.5 }}
                    }}
                }}];
                var wordLayout = {{
                    title: '',
                    xaxis: {{ title: 'Words' }},
                    yaxis: {{ title: 'Frequency' }},
                    plot_bgcolor: '#fafafa',
                    paper_bgcolor: '#fafafa'
                }};
                Plotly.newPlot('wordChart', wordData, wordLayout, {{responsive: true}});
            </script>
        </div>"""

                                        # Sentiment Distribution Chart
                                        if 'sentiment' in results_data and 'distribution' in results_data['sentiment']:
                                            dist = results_data['sentiment']['distribution']
                                            html += f"""
        <div class="chart-container">
            <h3>😊 Sentiment Distribution</h3>
            <div id="sentimentChart"></div>
            <script>
                var sentimentData = [{{
                    values: [{dist.get('POSITIVE', 0)}, {dist.get('NEUTRAL', 0)}, {dist.get('NEGATIVE', 0)}],
                    labels: ['Positive', 'Neutral', 'Negative'],
                    type: 'pie',
                    marker: {{
                        colors: ['#4caf50', '#ff9800', '#f44336']
                    }}
                }}];
                var sentimentLayout = {{
                    title: '',
                    plot_bgcolor: '#fafafa',
                    paper_bgcolor: '#fafafa'
                }};
                Plotly.newPlot('sentimentChart', sentimentData, sentimentLayout, {{responsive: true}});
            </script>
        </div>"""

                                        # Participant Activity Chart
                                        if conv.participants:
                                            participant_counts = {}
                                            for msg in conv.messages:
                                                participant_counts[msg.sender] = participant_counts.get(msg.sender, 0) + 1

                                            participants = list(participant_counts.keys())[:10]
                                            messages = [participant_counts[p] for p in participants]

                                            html += f"""
        <div class="chart-container">
            <h3>👥 Top 10 Participants Activity</h3>
            <div id="participantChart"></div>
            <script>
                var participantData = [{{
                    x: {json.dumps(messages)},
                    y: {json.dumps(participants)},
                    type: 'bar',
                    orientation: 'h',
                    marker: {{
                        color: 'rgb(118, 75, 162)',
                        line: {{ color: 'rgb(76, 48, 108)', width: 1.5 }}
                    }}
                }}];
                var participantLayout = {{
                    title: '',
                    xaxis: {{ title: 'Message Count' }},
                    yaxis: {{ title: 'Participant' }},
                    plot_bgcolor: '#fafafa',
                    paper_bgcolor: '#fafafa'
                }};
                Plotly.newPlot('participantChart', participantData, participantLayout, {{responsive: true}});
            </script>
        </div>"""

                                        # Timeline Chart (if timestamps available)
                                        try:
                                            from collections import Counter
                                            dates = [msg.timestamp.strftime('%Y-%m-%d') for msg in conv.messages if msg.timestamp]
                                            if dates:
                                                date_counts = Counter(dates)
                                                sorted_dates = sorted(date_counts.items())
                                                timeline_dates = [d[0] for d in sorted_dates]
                                                timeline_counts = [d[1] for d in sorted_dates]

                                                html += f"""
        <div class="chart-container">
            <h3>📅 Message Timeline</h3>
            <div id="timelineChart"></div>
            <script>
                var timelineData = [{{
                    x: {json.dumps(timeline_dates)},
                    y: {json.dumps(timeline_counts)},
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: {{ color: 'rgb(102, 126, 234)', width: 2 }},
                    marker: {{ size: 8, color: 'rgb(118, 75, 162)' }}
                }}];
                var timelineLayout = {{
                    title: '',
                    xaxis: {{ title: 'Date' }},
                    yaxis: {{ title: 'Messages' }},
                    plot_bgcolor: '#fafafa',
                    paper_bgcolor: '#fafafa'
                }};
                Plotly.newPlot('timelineChart', timelineData, timelineLayout, {{responsive: true}});
            </script>
        </div>"""
                                        except:
                                            pass

                                        html += """
    </div>
</body>
</html>"""
                                        return html

                                    html_report = generate_html_report(conversation, results)
                                    st.download_button(
                                        label="🌐 Download Interactive HTML",
                                        data=html_report,
                                        file_name=f"analytics_{conversation.id}.html",
                                        mime="text/html",
                                        help="Download full analytics with interactive charts (Plotly). Works offline!",
                                        use_container_width=True
                                    )

                                with col2:
                                    # JSON download
                                    import json
                                    json_data = json.dumps(results, indent=2, default=str)
                                    st.download_button(
                                        label="📄 Download JSON",
                                        data=json_data,
                                        file_name=f"analytics_{conversation.id}.json",
                                        mime="application/json",
                                        help="Download raw analytics data as JSON",
                                        use_container_width=True
                                    )

                                with col3:
                                    # Text report download
                                    text_report = analytics_engine.generate_report(conversation)
                                    st.download_button(
                                        label="📝 Download TXT",
                                        data=text_report,
                                        file_name=f"analytics_{conversation.id}.txt",
                                        mime="text/plain",
                                        help="Download formatted text report",
                                        use_container_width=True
                                    )

                                with col4:
                                    # CSV download (summary data)
                                    import pandas as pd
                                    import io

                                    # Prepare summary data for CSV
                                    csv_data = []

                                    # Add conversation info
                                    csv_data.append(['Conversation ID', conversation.id])
                                    csv_data.append(['Title', conversation.title])
                                    csv_data.append(['Platform', conversation.platform])
                                    csv_data.append(['Total Messages', len(conversation.messages)])
                                    csv_data.append([''])

                                    # Add call log data if available
                                    if 'call_log' in results and results['call_log'].get('is_call_log'):
                                        call_data = results['call_log']
                                        csv_data.append(['Call Log Analysis', ''])
                                        csv_data.append(['Total Calls', call_data.get('total_calls', 0)])
                                        csv_data.append(['Completed Calls', call_data.get('completed_calls', 0)])
                                        csv_data.append(['Missed Calls', call_data.get('missed_calls', 0)])
                                        csv_data.append([''])

                                    # Create CSV
                                    csv_buffer = io.StringIO()
                                    import csv
                                    writer = csv.writer(csv_buffer)
                                    writer.writerows(csv_data)
                                    csv_str = csv_buffer.getvalue()

                                    st.download_button(
                                        label="📊 Download CSV",
                                        data=csv_str,
                                        file_name=f"analytics_{conversation.id}.csv",
                                        mime="text/csv",
                                        help="Download analytics summary as CSV",
                                        use_container_width=True
                                    )

                            # Cleanup temp file (only if we created one)
                            if not demo_conversation and input_path and os.path.exists(input_path):
                                os.unlink(input_path)

                        except Exception as e:
                            st.error(f"❌ Analysis failed: {e}")
                            import traceback
                            with st.expander("Show traceback"):
                                st.code(traceback.format_exc())
                            # Cleanup on error
                            if not demo_conversation and input_path and os.path.exists(input_path):
                                os.unlink(input_path)

                # Show conversion preview and download at the end
                if conversion_result:
                    st.markdown("---")
                    st.header("📥 Download Converted File")
                    preview_content(conversion_result['output_path'], conversion_result['format'])

                    st.markdown("---")

                    # Download button
                    st.download_button(
                        label=f"📥 Download {conversion_result['output_filename']}",
                        data=conversion_result['output_data'],
                        file_name=conversion_result['output_filename'],
                        mime=get_mime_type(conversion_result['format']),
                        use_container_width=True
                    )

                    # Cleanup output file
                    if os.path.exists(conversion_result['output_path']):
                        os.unlink(conversion_result['output_path'])

    else:
        # No file uploaded - show getting started
        st.info("👆 **Upload any file to get started!**")

        st.markdown("### 🚀 How It Works")
        st.markdown("""
        1. **Upload** any text content (chats, documents, notes, transcripts, etc.)
        2. **Choose** what you want to do:
           - 🔄 Convert to another format
           - 📊 Analyze with AI/keywords
           - ✨ Both!
        3. **Preview** results right here in the browser
        4. **Download** your converted file

        **✨ Versatile:** Works with chats, documents, articles, meeting notes, and more!
        """)

        st.markdown("### 🔒 Privacy & Roadmap")
        st.markdown("""
        **Coming Soon:**
        - ✅ PII/PHI redaction (strip personal info)
        - ✅ Privacy checkbox (remove sensitive data)
        - ✅ Custom redaction rules
        - ✅ GDPR compliance tools

        Your data is processed in memory and automatically deleted after conversion.
        """)


def get_mime_type(format_ext):
    """Get MIME type for download button."""
    mime_types = {
        'html': 'text/html',
        'md': 'text/markdown',
        'markdown': 'text/markdown',
        'json': 'application/json',
        'txt': 'text/plain',
        'text': 'text/plain',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'db': 'application/x-sqlite3',
        'sqlite': 'application/x-sqlite3',
        'xmind': 'application/zip'
    }
    return mime_types.get(format_ext, 'application/octet-stream')


if __name__ == "__main__":
    main()
