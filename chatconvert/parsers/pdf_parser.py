"""
PDF Parser - Extract and parse chat conversations from PDF files.

Attempts to extract text from PDF and parse it as chat conversation.
Supports PDFs containing:
- WhatsApp exports
- Discord chat logs
- Generic chat transcripts
- Text-based conversation logs
"""

import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class PDFParser(BaseParser):
    """
    Parse chat conversations from PDF files.

    Extracts text from PDF and attempts to identify chat message patterns.
    Works best with PDFs that contain:
    - Timestamped messages
    - Sender names/identifiers
    - Clear message structure
    """

    def __init__(self):
        """Initialize PDF parser."""
        super().__init__()
        self.use_pdfplumber = HAS_PDFPLUMBER
        self.use_pypdf2 = HAS_PYPDF2

        if not (self.use_pdfplumber or self.use_pypdf2):
            self.logger.warning("Neither pdfplumber nor PyPDF2 available. PDF parsing will fail.")

    def can_parse(self, file_path: str) -> bool:
        """Check if file is a PDF."""
        ext = self._get_file_extension(file_path)
        return ext in ['pdf'] and (self.use_pdfplumber or self.use_pypdf2)

    def parse(self, file_path: str) -> Conversation:
        """
        Parse a PDF file containing chat conversation.

        Args:
            file_path: Path to PDF file

        Returns:
            Conversation object with messages

        Raises:
            ImportError: If neither pdfplumber nor PyPDF2 is installed
            ValueError: If PDF cannot be parsed or contains no text
        """
        if not (self.use_pdfplumber or self.use_pypdf2):
            raise ImportError("PDF parsing requires pdfplumber or PyPDF2. Install with: pip install pdfplumber")

        file_path = Path(file_path)
        self.logger.info(f"Parsing PDF: {file_path}")

        # Extract text from PDF
        text = self._extract_text(file_path)

        if not text or not text.strip():
            raise ValueError("PDF contains no extractable text")

        # Try to detect and parse chat format
        messages = self._parse_chat_text(text)

        if not messages:
            # Fallback: treat entire PDF as a single message
            self.logger.warning("Could not detect chat format, treating as single text block")
            messages = [Message(
                id="1",
                sender="Unknown",
                content=text[:5000],  # Limit to first 5000 chars
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
            platform="PDF Export",
            conversation_type="unknown",
            created_at=messages[0].timestamp if messages else datetime.now()
        )

        self.logger.info(f"Parsed {len(messages)} messages from PDF")
        return conversation

    def _extract_text(self, file_path: Path) -> str:
        """Extract all text from PDF."""
        # Try pdfplumber first (more reliable)
        if self.use_pdfplumber:
            try:
                import pdfplumber
                text_parts = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return '\n'.join(text_parts)
            except Exception as e:
                self.logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")

        # Fallback to PyPDF2
        if self.use_pypdf2:
            try:
                text_parts = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return '\n'.join(text_parts)
            except Exception as e:
                self.logger.error(f"PyPDF2 extraction failed: {e}")
                raise ValueError(f"Failed to extract text from PDF: {e}")

        return ""

    def _parse_chat_text(self, text: str) -> List[Message]:
        """
        Parse extracted text as chat messages.

        Tries to detect common chat patterns:
        - [Timestamp] Sender: Message
        - Timestamp - Sender: Message
        - Sender (Timestamp): Message
        """
        messages = []

        # Pattern 1: [HH:MM] Sender: Message or [YYYY-MM-DD HH:MM] Sender: Message
        pattern1 = r'\[([^\]]+)\]\s*([^:]+?):\s*(.+?)(?=\n\[|\Z)'

        # Pattern 2: Sender (Timestamp): Message
        pattern2 = r'([^(]+?)\s*\(([^)]+)\):\s*(.+?)(?=\n[^(]+?\s*\(|\Z)'

        # Pattern 3: Timestamp - Sender: Message
        pattern3 = r'(\d{1,4}[-/]\d{1,2}[-/]\d{1,4}[^\-]*)\s*-\s*([^:]+?):\s*(.+?)(?=\n\d|\Z)'

        for pattern_num, pattern in enumerate([pattern1, pattern2, pattern3], 1):
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            temp_messages = []

            for match in matches:
                if pattern_num == 1:
                    timestamp_str, sender, content = match.groups()
                elif pattern_num == 2:
                    sender, timestamp_str, content = match.groups()
                else:  # pattern 3
                    timestamp_str, sender, content = match.groups()

                # Parse timestamp
                timestamp = self._parse_timestamp(timestamp_str)

                # Clean content
                content = content.strip()

                if content:  # Only add non-empty messages
                    temp_messages.append(Message(
                        id=str(len(temp_messages) + 1),
                        sender=sender.strip(),
                        content=content,
                        timestamp=timestamp,
                        type=MessageType.TEXT
                    ))

            # If we found messages with this pattern, use them
            if temp_messages:
                self.logger.info(f"Detected chat format using pattern {pattern_num}")
                return temp_messages

        # If no patterns matched, return empty (will trigger fallback)
        return []

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime."""
        timestamp_str = timestamp_str.strip()

        # Common timestamp formats
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

        # If all parsing fails, use current time
        self.logger.warning(f"Could not parse timestamp: {timestamp_str}")
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
