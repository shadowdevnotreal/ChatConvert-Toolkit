"""
HTML Converter - Create beautiful interactive HTML pages from conversations.

Features:
- Responsive design with gradient styling
- Smooth animations
- Message grouping by participant
- Statistics footer
- Custom scrollbar styling
- Mobile-friendly layout
"""

import time
from html import escape
from pathlib import Path

from .base_converter import BaseConverter
from ..models import Conversation, ConversionResult, Message


class HTMLConverter(BaseConverter):
    """Convert conversations to beautiful HTML format."""

    def get_file_extension(self) -> str:
        return 'html'

    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert conversation to styled HTML.

        Config options:
        - theme: 'gradient' (default), 'light', 'dark'
        - animate: Enable animations (default: True)
        - show_stats: Show statistics footer (default: True)

        Args:
            conversation: Conversation to convert
            output_file: Path to output .html file

        Returns:
            ConversionResult
        """
        start_time = time.time()
        path = self._validate_output_path(output_file)

        try:
            # Get config
            theme = self.config.get('theme', 'gradient')
            animate = self.config.get('animate', True)
            show_stats = self.config.get('show_stats', True)

            # Generate HTML
            html_content = self._generate_html(
                conversation,
                theme=theme,
                animate=animate,
                show_stats=show_stats
            )

            # Write to file
            self._write_file(path, html_content)

            processing_time = time.time() - start_time

            return self._create_result(
                success=True,
                output_file=str(path),
                message_count=len(conversation.messages),
                processing_time=processing_time,
                statistics={
                    'theme': theme,
                    'participants': len(conversation.get_participants_list()),
                }
            )

        except Exception as e:
            self.logger.error(f"HTML conversion failed: {e}")
            return self._create_result(
                success=False,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _generate_html(
        self,
        conversation: Conversation,
        theme: str = 'gradient',
        animate: bool = True,
        show_stats: bool = True
    ) -> str:
        """Generate complete HTML document."""

        # Get statistics
        participants = conversation.get_participants_list()
        date_range = conversation.get_date_range()

        # Build HTML
        html = self._get_html_header(conversation.title, theme, animate)
        html += self._get_messages_html(conversation.messages)

        if show_stats:
            html += self._get_stats_html(conversation, participants, date_range)

        html += self._get_html_footer()

        return html

    def _get_html_header(self, title: str, theme: str, animate: bool) -> str:
        """Generate HTML header with styling."""

        animation_css = """
        .message {
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        """ if animate else ""

        # Theme colors
        if theme == 'dark':
            bg_gradient = "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)"
            header_bg = "linear-gradient(135deg, #0f3460 0%, #16213e 100%)"
            container_bg = "#1a1a2e"
            text_color = "#e5e5e5"
            accent_color = "#e94560"
        elif theme == 'light':
            bg_gradient = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
            header_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            container_bg = "white"
            text_color = "#333"
            accent_color = "#667eea"
        else:  # gradient (default)
            bg_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            header_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            container_bg = "white"
            text_color = "#333"
            accent_color = "#667eea"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: {bg_gradient};
            min-height: 100vh;
            padding: 20px;
            color: {text_color};
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: {container_bg};
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: {header_bg};
            color: white;
            padding: 25px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 5px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .chat-container {{
            padding: 30px;
            max-height: 700px;
            overflow-y: auto;
        }}

        .message {{
            margin-bottom: 20px;
        }}

        {animation_css}

        .message-header {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}

        .username {{
            font-weight: bold;
            color: {accent_color};
            margin-right: 10px;
            font-size: 15px;
        }}

        .timestamp {{
            font-size: 12px;
            color: #999;
        }}

        .message-content {{
            background: #f7f7f7;
            padding: 12px 15px;
            border-radius: 10px;
            border-left: 3px solid {accent_color};
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .message:nth-child(even) .message-content {{
            background: #e8eaf6;
            border-left-color: #764ba2;
        }}

        .message:nth-child(even) .username {{
            color: #764ba2;
        }}

        /* Attachment styles */
        .attachments {{
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .attachment {{
            border-radius: 8px;
            overflow: hidden;
            background: white;
            border: 1px solid #e0e0e0;
            max-width: 100%;
        }}

        .image-attachment img {{
            max-width: 400px;
            max-height: 300px;
            width: auto;
            height: auto;
            display: block;
            cursor: zoom-in;
            transition: transform 0.2s;
        }}

        .image-attachment img:hover {{
            transform: scale(1.02);
        }}

        .image-attachment img.fullscreen {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            max-width: 90vw;
            max-height: 90vh;
            z-index: 9999;
            cursor: zoom-out;
            box-shadow: 0 0 50px rgba(0,0,0,0.5);
        }}

        .video-attachment video {{
            max-width: 400px;
            width: 100%;
            display: block;
        }}

        .audio-attachment audio {{
            width: 300px;
            display: block;
        }}

        .attachment-name {{
            padding: 8px;
            font-size: 12px;
            color: #666;
            background: #f5f5f5;
        }}

        .attachment-info {{
            padding: 4px 8px;
            font-size: 11px;
            color: #999;
        }}

        .file-attachment {{
            padding: 10px;
            min-width: 200px;
        }}

        .stats {{
            background: #f9f9f9;
            padding: 20px 30px;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }}

        .stats h3 {{
            margin-bottom: 15px;
            color: {accent_color};
            font-size: 18px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .stat-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid {accent_color};
        }}

        .stat-label {{
            font-size: 12px;
            text-transform: uppercase;
            color: #999;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            color: {accent_color};
        }}

        /* Scrollbar styling */
        .chat-container::-webkit-scrollbar {{
            width: 8px;
        }}

        .chat-container::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}

        .chat-container::-webkit-scrollbar-thumb {{
            background: {accent_color};
            border-radius: 4px;
        }}

        .chat-container::-webkit-scrollbar-thumb:hover {{
            background: #764ba2;
        }}

        /* Mobile responsiveness */
        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}

            .chat-container {{
                padding: 15px;
            }}

            .header h1 {{
                font-size: 22px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 {escape(title)}</h1>
            <p>Chat Conversation</p>
        </div>

        <div class="chat-container">
"""

    def _get_messages_html(self, messages: list) -> str:
        """Generate HTML for all messages with media attachments."""
        html = ""

        for msg in messages:
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            username = escape(msg.sender)
            content = escape(msg.content)

            # Add attachments (images, videos, audio) if present
            attachments_html = ""
            if msg.attachments:
                attachments_html = '<div class="attachments">'
                for att in msg.attachments:
                    if att.is_image() and att.get_data_uri():
                        # Display image inline using data URI
                        attachments_html += f'''
                        <div class="attachment image-attachment">
                            <img src="{att.get_data_uri()}" alt="{escape(att.filename)}"
                                 onclick="this.classList.toggle('fullscreen')"
                                 title="Click to enlarge - {escape(att.filename)}">
                            <div class="attachment-name">📷 {escape(att.filename)}</div>
                        </div>
                        '''
                    elif att.is_video() and att.get_data_uri():
                        # Display video inline
                        attachments_html += f'''
                        <div class="attachment video-attachment">
                            <video controls>
                                <source src="{att.get_data_uri()}" type="{att.mime_type}">
                                Your browser doesn't support video playback.
                            </video>
                            <div class="attachment-name">🎥 {escape(att.filename)}</div>
                        </div>
                        '''
                    elif att.is_audio() and att.get_data_uri():
                        # Display audio player
                        attachments_html += f'''
                        <div class="attachment audio-attachment">
                            <audio controls>
                                <source src="{att.get_data_uri()}" type="{att.mime_type}">
                                Your browser doesn't support audio playback.
                            </audio>
                            <div class="attachment-name">🎵 {escape(att.filename)}</div>
                        </div>
                        '''
                    else:
                        # Generic file attachment
                        attachments_html += f'''
                        <div class="attachment file-attachment">
                            <div class="attachment-name">📎 {escape(att.filename)}</div>
                            <div class="attachment-info">{att.mime_type or "Unknown type"}</div>
                        </div>
                        '''
                attachments_html += '</div>'

            html += f"""
            <div class="message">
                <div class="message-header">
                    <span class="username">{username}</span>
                    <span class="timestamp">{timestamp}</span>
                </div>
                <div class="message-content">{content}</div>
                {attachments_html}
            </div>
"""

        return html

    def _get_stats_html(self, conversation: Conversation, participants: list, date_range: tuple) -> str:
        """Generate statistics footer HTML."""

        # Calculate per-participant stats
        participant_stats = {}
        for p in participants:
            count = sum(1 for m in conversation.messages if m.sender == p)
            participant_stats[p] = count

        # Format date range
        date_str = "Unknown"
        if date_range[0]:
            start = date_range[0].strftime('%Y-%m-%d')
            end = date_range[1].strftime('%Y-%m-%d')
            if start == end:
                date_str = start
            else:
                date_str = f"{start} to {end}"

        # Top participant
        top_participant = max(participant_stats.items(), key=lambda x: x[1]) if participant_stats else ("Unknown", 0)

        html = f"""
        </div>

        <div class="stats">
            <h3>📊 Conversation Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">Total Messages</div>
                    <div class="stat-value">{len(conversation.messages)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Participants</div>
                    <div class="stat-value">{len(participants)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Date Range</div>
                    <div class="stat-value" style="font-size: 14px;">{escape(date_str)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Most Active</div>
                    <div class="stat-value" style="font-size: 16px;">{escape(top_participant[0])} ({top_participant[1]})</div>
                </div>
            </div>
        </div>
"""

        return html

    def _get_html_footer(self) -> str:
        """Generate HTML footer."""
        return """
    </div>
</body>
</html>
"""
