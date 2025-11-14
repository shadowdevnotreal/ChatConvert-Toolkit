"""
HTML Parser - Extract and parse chat conversations from HTML files.

Parses chat content from HTML files including:
- Saved web pages with chat history
- Email thread exports
- Forum conversation exports
- Browser-saved Discord/Slack conversations
"""

from pathlib import Path
from typing import List
from datetime import datetime
import re

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class HTMLParser(BaseParser):
    """
    Parse chat conversations from HTML files.

    Extracts text from HTML and identifies chat message patterns.
    Handles various HTML structures from different platforms.
    """

    def __init__(self):
        """Initialize HTML parser."""
        super().__init__()

        if not HAS_BS4:
            self.logger.warning("BeautifulSoup not available. HTML parsing will fail.")

    def can_parse(self, file_path: str) -> bool:
        """Check if file is an HTML file."""
        ext = self._get_file_extension(file_path)
        return ext in ['html', 'htm'] and HAS_BS4

    def parse(self, file_path: str) -> Conversation:
        """
        Parse an HTML file containing chat conversation.

        Args:
            file_path: Path to HTML file

        Returns:
            Conversation object with messages

        Raises:
            ImportError: If beautifulsoup4 is not installed
            ValueError: If HTML cannot be parsed
        """
        if not HAS_BS4:
            raise ImportError("HTML parsing requires beautifulsoup4. Install with: pip install beautifulsoup4")

        file_path = Path(file_path)
        self.logger.info(f"Parsing HTML: {file_path}")

        # Parse HTML
        soup = self._parse_html(file_path)

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        if not text:
            raise ValueError("HTML contains no text")

        # Try to parse chat messages
        messages = self._parse_chat_text(text)

        if not messages:
            # Fallback: treat entire content as single message
            self.logger.warning("Could not detect chat format, treating as single text block")
            messages = [Message(
                id="1",
                sender="Unknown",
                content=text[:5000],
                timestamp=datetime.now(),
                type=MessageType.TEXT
            )]

        # Extract participants
        participants = self._extract_participants(messages)

        conversation = Conversation(
            id=file_path.stem,
            title=file_path.stem,
            messages=messages,
            participants=participants,
            platform="HTML Export",
            conversation_type="unknown",
            created_at=messages[0].timestamp if messages else datetime.now()
        )

        self.logger.info(f"Parsed {len(messages)} messages from HTML")
        return conversation

    def _parse_html(self, file_path: Path):
        """Parse HTML file with BeautifulSoup."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return BeautifulSoup(content, 'html.parser')
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return BeautifulSoup(content, 'html.parser')
            except Exception as e:
                self.logger.error(f"Failed to parse HTML: {e}")
                raise ValueError(f"Failed to read HTML file: {e}")

    def _parse_chat_text(self, text: str) -> List[Message]:
        """Parse extracted text as chat messages."""
        messages = []

        # Pattern 1: [Timestamp] Sender: Message
        pattern1 = r'\[([^\]]+)\]\s*([^:]+?):\s*(.+?)(?=\n\[|\Z)'

        # Pattern 2: Sender (Timestamp): Message
        pattern2 = r'([^(]+?)\s*\(([^)]+)\):\s*(.+?)(?=\n[^(]+?\s*\(|\Z)'

        # Pattern 3: Timestamp - Sender: Message
        pattern3 = r'(\d{1,4}[-/]\d{1,2}[-/]\d{1,4}[^\-]*)\s*-\s*([^:]+?):\s*(.+?)(?=\n\d|\Z)'

        # Pattern 4: Simple "Sender: Message"
        pattern4 = r'^([A-Z][a-zA-Z0-9_\s]{1,30}):\s*(.+?)$'

        for pattern_num, pattern in enumerate([pattern1, pattern2, pattern3], 1):
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            temp_messages = []

            for match in matches:
                if pattern_num == 1:
                    timestamp_str, sender, content = match.groups()
                    timestamp = self._parse_timestamp(timestamp_str)
                elif pattern_num == 2:
                    sender, timestamp_str, content = match.groups()
                    timestamp = self._parse_timestamp(timestamp_str)
                else:
                    timestamp_str, sender, content = match.groups()
                    timestamp = self._parse_timestamp(timestamp_str)

                content = content.strip()
                if content:
                    temp_messages.append(Message(
                        id=str(len(temp_messages) + 1),
                        sender=sender.strip(),
                        content=content,
                        timestamp=timestamp,
                        type=MessageType.TEXT
                    ))

            if temp_messages:
                self.logger.info(f"Detected chat format using pattern {pattern_num}")
                return temp_messages

        # Try simple pattern (no timestamp)
        lines = text.split('\n')
        temp_messages = []
        for line in lines:
            match = re.match(pattern4, line.strip())
            if match:
                sender, content = match.groups()
                temp_messages.append(Message(
                    id=str(len(temp_messages) + 1),
                    sender=sender.strip(),
                    content=content.strip(),
                    timestamp=datetime.now(),
                    type=MessageType.TEXT
                ))

        if temp_messages:
            self.logger.info("Detected simple chat format")
            return temp_messages

        return []

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime."""
        timestamp_str = timestamp_str.strip()

        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%H:%M:%S',
            '%H:%M',
            '%I:%M %p',
            '%I:%M:%S %p',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        return datetime.now()

    def _extract_participants(self, messages: List[Message]) -> List[Participant]:
        """Extract unique participants from messages."""
        senders = set(msg.sender for msg in messages)
        return [
            Participant(
                id=sender.lower().replace(' ', '_'),
                username=sender,
                display_name=sender
            )
            for sender in sorted(senders)
        ]
