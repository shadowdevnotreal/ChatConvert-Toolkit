"""
Markdown Parser - Extract and parse chat conversations from Markdown files.

Parses chat content from .md files including:
- GitHub/GitLab conversation exports
- Note-taking apps (Obsidian, Notion, etc.)
- Markdown-formatted chat logs
- Meeting transcripts
"""

from pathlib import Path
from typing import List
from datetime import datetime
import re

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class MarkdownParser(BaseParser):
    """
    Parse chat conversations from Markdown (.md) files.

    Extracts text from markdown and identifies chat message patterns.
    """

    def can_parse(self, file_path: str) -> bool:
        """Check if file is a Markdown file."""
        ext = self._get_file_extension(file_path)
        return ext in ['md', 'markdown']

    def parse(self, file_path: str) -> Conversation:
        """
        Parse a Markdown file containing chat conversation.

        Args:
            file_path: Path to .md file

        Returns:
            Conversation object with messages

        Raises:
            ValueError: If file cannot be parsed
        """
        file_path = Path(file_path)
        self.logger.info(f"Parsing Markdown: {file_path}")

        # Read markdown file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()

        if not text.strip():
            raise ValueError("Markdown file is empty")

        # Parse messages
        messages = self._parse_chat_text(text)

        if not messages:
            # Fallback: treat as single message
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
            platform="Markdown Export",
            conversation_type="unknown",
            created_at=messages[0].timestamp if messages else datetime.now()
        )

        self.logger.info(f"Parsed {len(messages)} messages from Markdown")
        return conversation

    def _parse_chat_text(self, text: str) -> List[Message]:
        """Parse markdown text as chat messages."""
        messages = []

        # Pattern 1: [Timestamp] Sender: Message
        pattern1 = r'\[([^\]]+)\]\s*([^:]+?):\s*(.+?)(?=\n\[|\Z)'

        # Pattern 2: **Sender** (Timestamp): Message
        pattern2 = r'\*\*([^*]+)\*\*\s*\(([^)]+)\):\s*(.+?)(?=\n\*\*|\Z)'

        # Pattern 3: ## Sender - Timestamp
        pattern3 = r'^##\s+([^-]+?)\s*-\s*([^\n]+)\n(.+?)(?=\n##|\Z)'

        # Pattern 4: > Sender: Message (blockquote style)
        pattern4 = r'^>\s*([^:]+?):\s*(.+?)$'

        # Pattern 5: - Sender: Message (list style)
        pattern5 = r'^[-*]\s*([^:]+?):\s*(.+?)$'

        for pattern_num, pattern in enumerate([pattern1, pattern2, pattern3], 1):
            flags = re.MULTILINE | re.DOTALL
            matches = re.finditer(pattern, text, flags)
            temp_messages = []

            for match in matches:
                if pattern_num == 1:
                    timestamp_str, sender, content = match.groups()
                    timestamp = self._parse_timestamp(timestamp_str)
                elif pattern_num == 2:
                    sender, timestamp_str, content = match.groups()
                    timestamp = self._parse_timestamp(timestamp_str)
                else:  # pattern 3
                    sender, timestamp_str, content = match.groups()
                    timestamp = self._parse_timestamp(timestamp_str)

                content = content.strip()
                # Remove markdown formatting from content
                content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Bold
                content = re.sub(r'\*([^*]+)\*', r'\1', content)      # Italic
                content = re.sub(r'`([^`]+)`', r'\1', content)        # Code

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

        # Try blockquote or list patterns
        lines = text.split('\n')
        temp_messages = []

        for line in lines:
            # Try blockquote pattern
            match = re.match(pattern4, line.strip())
            if not match:
                # Try list pattern
                match = re.match(pattern5, line.strip())

            if match:
                groups = match.groups()
                if len(groups) == 2:
                    sender, content = groups
                    temp_messages.append(Message(
                        id=str(len(temp_messages) + 1),
                        sender=sender.strip(),
                        content=content.strip(),
                        timestamp=datetime.now(),
                        type=MessageType.TEXT
                    ))

        if temp_messages:
            self.logger.info("Detected blockquote/list chat format")
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
