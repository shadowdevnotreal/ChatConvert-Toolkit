"""
Generic Text Parser - Parse chat conversations from plain text files.

Handles .txt files that may contain various chat formats:
- WhatsApp exports
- Generic timestamp-based chats
- Simple "Name: Message" format
- Discord/Slack copy-paste
- Any plain text conversation

Falls back to treating entire file as text if no pattern matches.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class GenericTextParser(BaseParser):
    """
    Parse chat conversations from generic text files.

    Attempts multiple chat format patterns and provides fallback
    for unstructured text.
    """

    def can_parse(self, file_path: str) -> bool:
        """Check if file is a text file."""
        ext = self._get_file_extension(file_path)
        return ext in ['txt', 'text', 'log']

    def parse(self, file_path: str) -> Conversation:
        """
        Parse a text file containing chat conversation.

        Args:
            file_path: Path to text file

        Returns:
            Conversation object with messages

        Raises:
            ValueError: If file cannot be parsed
        """
        file_path = Path(file_path)
        self.logger.info(f"Parsing text file: {file_path}")

        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()

        if not text.strip():
            raise ValueError("Text file is empty")

        # Try to parse as chat messages
        messages = self._parse_chat_text(text)

        if not messages:
            # Fallback: treat as plain text document/article/notes
            self.logger.info("No chat format detected - treating as plain text document")

            # Detect if this looks like a document vs chat
            # Heuristic: If text has multiple paragraphs and no sender patterns, likely a document
            is_document = '\n\n' in text or len(text) > 1000

            sender = "Document" if is_document else "Unknown"
            platform = "Document" if is_document else "Text File"

            # Split long text into multiple messages (100k chars each to avoid memory issues)
            chunk_size = 100000
            text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

            for idx, chunk in enumerate(text_chunks):
                messages.append(Message(
                    id=str(idx + 1),
                    sender=sender,
                    content=chunk,
                    timestamp=datetime.now(),
                    type=MessageType.TEXT,
                    platform=platform
                ))

            self.logger.info(f"Processed as {platform.lower()} with {len(messages)} chunk(s)")

        # Extract participants
        participants = self._extract_participants(messages)

        conversation = Conversation(
            id=file_path.stem,
            title=file_path.stem.replace('_', ' ').title(),
            messages=messages,
            participants=participants,
            platform="Text File",
            conversation_type="chat",
            created_at=messages[0].timestamp if messages else datetime.now()
        )

        conversation.sort_messages()
        self.logger.info(f"Parsed {len(messages)} messages from {len(participants)} participants")

        return conversation

    def _parse_chat_text(self, text: str) -> List[Message]:
        """Parse text using multiple chat format patterns."""

        # Pattern 1: WhatsApp iOS - [DD/MM/YY, HH:MM:SS] Sender: Message
        pattern1 = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.+?)(?=\n\[|\Z)'

        # Pattern 2: WhatsApp Android - DD/MM/YY, HH:MM - Sender: Message
        pattern2 = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.+?)(?=\n\d{1,2}/|\Z)'

        # Pattern 3: Generic timestamp - [YYYY-MM-DD HH:MM] Sender: Message
        pattern3 = r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.+?)(?=\n\[|\Z)'

        # Pattern 4: Discord/Slack style - Sender [HH:MM AM/PM]
        pattern4 = r'^([^\[\n]+?)\s*\[(\d{1,2}:\d{2}\s*[AP]M)\]\s*$\n(.+?)(?=\n[^\[\n]+?\s*\[|\Z)'

        # Pattern 5: Simple format - Sender: Message (line by line)
        pattern5 = r'^([^:\n]{2,30}):\s*(.+?)$'

        patterns = [
            (pattern1, 'WhatsApp iOS'),
            (pattern2, 'WhatsApp Android'),
            (pattern3, 'Generic Timestamp'),
            (pattern4, 'Discord/Slack'),
        ]

        # Try each pattern
        for pattern, format_name in patterns:
            messages = self._try_pattern(text, pattern, format_name)
            if messages and len(messages) >= 2:  # Need at least 2 messages to be valid
                return messages

        # Try simple line-by-line pattern
        messages = self._parse_simple_format(text, pattern5)
        if messages and len(messages) >= 2:
            return messages

        return []

    def _try_pattern(self, text: str, pattern: str, format_name: str) -> List[Message]:
        """Try parsing text with a specific pattern."""
        messages = []
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)

        for idx, match in enumerate(matches):
            groups = match.groups()

            try:
                if len(groups) == 4:  # Timestamp + Sender + Content patterns
                    timestamp_str, time_str, sender, content = groups
                    timestamp = self._parse_timestamp(f"{timestamp_str} {time_str}")
                elif len(groups) == 3:  # Other patterns
                    if format_name == 'Generic Timestamp':
                        timestamp_str, sender, content = groups
                        timestamp = self._parse_timestamp(timestamp_str)
                    elif format_name == 'Discord/Slack':
                        sender, time_str, content = groups
                        timestamp = self._parse_timestamp(time_str)
                    else:
                        continue
                else:
                    continue

                if content.strip():
                    messages.append(Message(
                        id=str(idx + 1),
                        sender=sender.strip(),
                        content=content.strip(),
                        timestamp=timestamp,
                        type=MessageType.TEXT,
                        platform=format_name
                    ))
            except Exception as e:
                self.logger.debug(f"Failed to parse match: {e}")
                continue

        if messages:
            self.logger.info(f"Detected {format_name} format with {len(messages)} messages")

        return messages

    def _parse_simple_format(self, text: str, pattern: str) -> List[Message]:
        """Parse simple 'Sender: Message' line-by-line format."""
        messages = []
        lines = text.split('\n')

        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                sender, content = match.groups()
                # Filter out likely non-chat lines
                if len(sender) < 2 or len(sender) > 30:
                    continue
                if sender.lower() in ['note', 'subject', 'from', 'to', 'date']:
                    continue

                messages.append(Message(
                    id=str(idx + 1),
                    sender=sender.strip(),
                    content=content.strip(),
                    timestamp=datetime.now(),
                    type=MessageType.TEXT,
                    platform="Simple Text"
                ))

        if messages:
            self.logger.info(f"Detected simple format with {len(messages)} messages")

        return messages

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse various timestamp formats."""
        timestamp_str = timestamp_str.strip()

        formats = [
            # WhatsApp formats
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %I:%M:%S %p',
            '%d/%m/%Y %I:%M %p',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            # Generic formats
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            # Time only formats
            '%H:%M %p',
            '%I:%M %p',
            '%H:%M:%S',
            '%H:%M',
        ]

        # Normalize date format for 2-digit years
        if '/' in timestamp_str:
            parts = timestamp_str.split()
            if parts and '/' in parts[0]:
                date_parts = parts[0].split('/')
                if len(date_parts) == 3 and len(date_parts[2]) == 2:
                    year = int(date_parts[2])
                    date_parts[2] = str(2000 + year) if year < 50 else str(1900 + year)
                    parts[0] = '/'.join(date_parts)
                    timestamp_str = ' '.join(parts)

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # If time-only, use today's date
        time_only_match = re.match(r'(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)', timestamp_str, re.IGNORECASE)
        if time_only_match:
            return datetime.now()

        # Fallback to now
        self.logger.debug(f"Could not parse timestamp: {timestamp_str}")
        return datetime.now()

    def _extract_participants(self, messages: List[Message]) -> List[Participant]:
        """Extract unique participants from messages."""
        participants_set = set(msg.sender for msg in messages)
        return [
            Participant(id=str(i), username=username)
            for i, username in enumerate(sorted(participants_set))
        ]
