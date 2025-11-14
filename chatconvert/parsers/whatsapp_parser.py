"""
WhatsApp Parser - Parse WhatsApp text export files.

Supports both iOS and Android export formats.

WhatsApp exports are plain text files with format:
- iOS: [DD/MM/YY, HH:MM:SS] Username: Message
- Android: DD/MM/YY, HH:MM - Username: Message

Media references are shown as <Media omitted>
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class WhatsAppParser(BaseParser):
    """Parse WhatsApp text export format."""

    # Regex patterns for different WhatsApp formats
    IOS_PATTERN = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.+)'
    ANDROID_PATTERN = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.+)'

    def can_parse(self, file_path: str) -> bool:
        """Check if file is WhatsApp text export format."""
        ext = self._get_file_extension(file_path)
        if ext not in ['txt', 'text']:
            return False

        # Check if content matches WhatsApp format
        try:
            content = self._read_file(file_path)
            lines = content.split('\n')[:10]  # Check first 10 lines

            for line in lines:
                if line.strip():
                    if re.match(self.IOS_PATTERN, line) or re.match(self.ANDROID_PATTERN, line):
                        return True

            return False
        except:
            return False

    def parse(self, file_path: str) -> Conversation:
        """
        Parse WhatsApp text export into Conversation object.

        Args:
            file_path: Path to WhatsApp export file

        Returns:
            Conversation object

        Raises:
            ValueError: If format is invalid
            FileNotFoundError: If file doesn't exist
        """
        self._validate_file(file_path)
        self.logger.info(f"Parsing WhatsApp file: {file_path}")

        try:
            content = self._read_file(file_path)
            lines = content.split('\n')

            # Detect format
            format_type = self._detect_format(lines)
            self.logger.info(f"Detected format: {format_type}")

            # Parse messages
            messages = []
            participants_set = set()
            current_message = None

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue

                # Try to parse as new message
                parsed = self._parse_line(line, format_type)

                if parsed:
                    # Save previous message
                    if current_message:
                        msg = self._create_message(current_message)
                        messages.append(msg)
                        participants_set.add(msg.sender)

                    # Start new message
                    current_message = parsed
                else:
                    # Continuation of previous message (multiline)
                    if current_message:
                        current_message['content'] += '\n' + line

            # Save last message
            if current_message:
                msg = self._create_message(current_message)
                messages.append(msg)
                participants_set.add(msg.sender)

            if not messages:
                raise ValueError("No valid messages found in WhatsApp export")

            # Create participants
            participants = [
                Participant(id=str(i), username=username)
                for i, username in enumerate(sorted(participants_set))
            ]

            # Create conversation
            conversation = Conversation(
                id=Path(file_path).stem,
                title=Path(file_path).stem.replace('_', ' ').title(),
                messages=messages,
                participants=participants,
                platform='WhatsApp',
                conversation_type='chat',
            )

            conversation.sort_messages()

            self.logger.info(f"Parsed {len(messages)} messages from {len(participants)} participants")

            return conversation

        except Exception as e:
            self.logger.error(f"WhatsApp parsing failed: {e}")
            raise

    def _detect_format(self, lines: List[str]) -> str:
        """
        Detect iOS or Android format.

        Args:
            lines: File lines

        Returns:
            'ios' or 'android'
        """
        for line in lines[:20]:  # Check first 20 lines
            if re.match(self.IOS_PATTERN, line):
                return 'ios'
            if re.match(self.ANDROID_PATTERN, line):
                return 'android'

        return 'ios'  # Default

    def _parse_line(self, line: str, format_type: str) -> Optional[dict]:
        """
        Parse a line into message components.

        Args:
            line: Line to parse
            format_type: 'ios' or 'android'

        Returns:
            Dict with date, time, sender, content or None if not a message line
        """
        pattern = self.IOS_PATTERN if format_type == 'ios' else self.ANDROID_PATTERN

        match = re.match(pattern, line)
        if not match:
            return None

        date_str, time_str, sender, content = match.groups()

        return {
            'date': date_str,
            'time': time_str,
            'sender': sender.strip(),
            'content': content.strip(),
        }

    def _create_message(self, data: dict) -> Message:
        """
        Create Message object from parsed data.

        Args:
            data: Parsed message data

        Returns:
            Message object
        """
        # Parse timestamp
        timestamp = self._parse_whatsapp_timestamp(data['date'], data['time'])

        # Check for media
        content = data['content']
        message_type = MessageType.TEXT

        if content in ['<Media omitted>', '<media omitted>', '‎image omitted', '‎video omitted',
                       '‎audio omitted', '‎document omitted', '‎sticker omitted']:
            message_type = MessageType.MEDIA

        return Message(
            id=f"wa_{timestamp.timestamp()}",
            timestamp=timestamp,
            sender=data['sender'],
            content=content,
            type=message_type,
            platform='WhatsApp',
        )

    def _parse_whatsapp_timestamp(self, date_str: str, time_str: str) -> datetime:
        """
        Parse WhatsApp timestamp.

        Args:
            date_str: Date string (DD/MM/YY or DD/MM/YYYY)
            time_str: Time string (HH:MM or HH:MM:SS, optionally with AM/PM)

        Returns:
            datetime object
        """
        # Normalize date format
        date_parts = date_str.split('/')
        if len(date_parts[2]) == 2:
            # Convert YY to YYYY
            year = int(date_parts[2])
            date_parts[2] = str(2000 + year) if year < 50 else str(1900 + year)
            date_str = '/'.join(date_parts)

        # Combine date and time
        datetime_str = f"{date_str} {time_str}"

        # Try various formats
        formats = [
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %I:%M:%S %p',
            '%d/%m/%Y %I:%M %p',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y %I:%M:%S %p',
            '%m/%d/%Y %I:%M %p',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Could not parse WhatsApp timestamp: {datetime_str}")
