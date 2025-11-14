"""
DOCX/DOC Parser - Extract and parse chat conversations from Word documents.

Parses text content from Word documents (.docx) and attempts to identify
chat message patterns. Common use cases:
- Users who paste chat logs into Word
- Exported conversations saved as DOCX
- Meeting transcripts and chat logs
"""

from pathlib import Path
from typing import List
from datetime import datetime
import re

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class DOCXParser(BaseParser):
    """
    Parse chat conversations from Word documents (.docx).

    Extracts text from DOCX and identifies chat message patterns.
    """

    def __init__(self):
        """Initialize DOCX parser."""
        super().__init__()

        if not HAS_DOCX:
            self.logger.warning("python-docx not available. DOCX parsing will fail.")

    def can_parse(self, file_path: str) -> bool:
        """Check if file is a DOCX/DOC file."""
        ext = self._get_file_extension(file_path)
        return ext in ['docx', 'doc'] and HAS_DOCX

    def parse(self, file_path: str) -> Conversation:
        """
        Parse a DOCX file containing chat conversation.

        Args:
            file_path: Path to DOCX file

        Returns:
            Conversation object with messages

        Raises:
            ImportError: If python-docx is not installed
            ValueError: If DOCX cannot be parsed
        """
        if not HAS_DOCX:
            raise ImportError("DOCX parsing requires python-docx. Install with: pip install python-docx")

        file_path = Path(file_path)
        self.logger.info(f"Parsing DOCX: {file_path}")

        # Extract text from DOCX
        text = self._extract_text(file_path)

        if not text or not text.strip():
            raise ValueError("DOCX contains no text")

        # Parse chat messages from text
        messages = self._parse_chat_text(text)

        if not messages:
            # Fallback: treat entire document as single message
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
            platform="DOCX Export",
            conversation_type="unknown",
            created_at=messages[0].timestamp if messages else datetime.now()
        )

        self.logger.info(f"Parsed {len(messages)} messages from DOCX")
        return conversation

    def _extract_text(self, file_path: Path) -> str:
        """Extract all text from DOCX."""
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return '\n'.join(paragraphs)
        except Exception as e:
            self.logger.error(f"Failed to extract text from DOCX: {e}")
            raise ValueError(f"Failed to read DOCX file: {e}")

    def _parse_chat_text(self, text: str) -> List[Message]:
        """Parse text as chat messages using common patterns."""
        messages = []

        # Pattern 1: [HH:MM] Sender: Message or [YYYY-MM-DD HH:MM] Sender: Message
        pattern1 = r'\[([^\]]+)\]\s*([^:]+?):\s*(.+?)(?=\n\[|\Z)'

        # Pattern 2: Sender (Timestamp): Message
        pattern2 = r'([^(]+?)\s*\(([^)]+)\):\s*(.+?)(?=\n[^(]+?\s*\(|\Z)'

        # Pattern 3: Timestamp - Sender: Message
        pattern3 = r'(\d{1,4}[-/]\d{1,2}[-/]\d{1,4}[^\-]*)\s*-\s*([^:]+?):\s*(.+?)(?=\n\d|\Z)'

        # Pattern 4: Simple "Sender: Message" (common in pasted chats)
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
                else:  # pattern 3
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
            self.logger.info("Detected simple chat format (Sender: Message)")
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
