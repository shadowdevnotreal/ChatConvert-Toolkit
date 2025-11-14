"""
JSON Parser - Parse JSON chat exports from various platforms.

Supports:
- Discord export format
- Slack export format
- Telegram export format
- Generic JSON with auto-detection
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class JSONParser(BaseParser):
    """Parse JSON format chat logs from various platforms."""

    def can_parse(self, file_path: str) -> bool:
        """Check if file is valid JSON format."""
        ext = self._get_file_extension(file_path)
        if ext != 'json':
            return False

        # Try to parse as JSON
        try:
            content = self._read_file(file_path)
            json.loads(content)
            return True
        except:
            return False

    def parse(self, file_path: str) -> Conversation:
        """
        Parse JSON file into Conversation object.

        Auto-detects platform (Discord, Slack, Telegram) and parses accordingly.

        Args:
            file_path: Path to JSON file

        Returns:
            Conversation object

        Raises:
            ValueError: If JSON format is invalid or unsupported
            FileNotFoundError: If file doesn't exist
        """
        self._validate_file(file_path)
        self.logger.info(f"Parsing JSON file: {file_path}")

        try:
            content = self._read_file(file_path)
            data = json.loads(content)

            # Detect platform
            platform = self._detect_platform(data)
            self.logger.info(f"Detected platform: {platform}")

            # Parse based on platform
            if platform == 'discord':
                return self._parse_discord(data, file_path)
            elif platform == 'slack':
                return self._parse_slack(data, file_path)
            elif platform == 'telegram':
                return self._parse_telegram(data, file_path)
            else:
                return self._parse_generic(data, file_path)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            self.logger.error(f"JSON parsing failed: {e}")
            raise

    def _detect_platform(self, data: Any) -> str:
        """
        Detect which platform the JSON export is from.

        Args:
            data: Parsed JSON data

        Returns:
            Platform name ('discord', 'slack', 'telegram', 'generic')
        """
        if isinstance(data, dict):
            # Discord: has 'guild' or 'messages' with 'author' field
            if 'guild' in data or (isinstance(data.get('messages'), list) and
                                   len(data['messages']) > 0 and
                                   'author' in data['messages'][0]):
                return 'discord'

            # Slack: has 'ok' and 'messages' or direct messages array
            if 'ok' in data or ('messages' in data and isinstance(data['messages'], list)):
                return 'slack'

            # Telegram: has 'type' == 'personal_chat' or 'chats'
            if data.get('type') in ['personal_chat', 'group', 'supergroup'] or 'chats' in data:
                return 'telegram'

        return 'generic'

    def _parse_discord(self, data: Dict[str, Any], file_path: str) -> Conversation:
        """
        Parse Discord JSON export format.

        Discord exports have this structure:
        {
          "guild": {"id": "...", "name": "..."},
          "channel": {"id": "...", "name": "...", "type": "..."},
          "messages": [
            {
              "id": "...",
              "type": 0,
              "content": "...",
              "author": {"id": "...", "name": "...", "discriminator": "..."},
              "timestamp": "2024-01-01T12:00:00.000+00:00",
              "attachments": [...],
              "reactions": [...]
            }
          ]
        }
        """
        # Extract metadata
        guild_name = data.get('guild', {}).get('name', 'Discord')
        channel_name = data.get('channel', {}).get('name', 'channel')
        title = f"{guild_name} - {channel_name}"

        messages_data = data.get('messages', [])

        if not messages_data:
            raise ValueError("No messages found in Discord export")

        # Parse messages
        messages = []
        participants_set = set()

        for msg_data in messages_data:
            try:
                # Skip non-message types (like joins, pins, etc.)
                if msg_data.get('type', 0) != 0:
                    continue

                # Extract author info
                author = msg_data.get('author', {})
                username = author.get('name', 'Unknown')
                discriminator = author.get('discriminator')
                if discriminator and discriminator != '0':
                    display_name = f"{username}#{discriminator}"
                else:
                    display_name = username

                # Parse timestamp
                timestamp_str = msg_data.get('timestamp', '')
                timestamp = self._parse_timestamp(timestamp_str)

                # Get content
                content = msg_data.get('content', '')

                # Handle attachments
                attachments = []
                for att in msg_data.get('attachments', []):
                    from ..models import Attachment
                    attachments.append(Attachment(
                        file_path=att.get('url', ''),
                        file_type=att.get('contentType', 'unknown'),
                        file_size=att.get('size', 0)
                    ))

                # Handle reactions
                reactions = []
                for react in msg_data.get('reactions', []):
                    from ..models import Reaction
                    emoji = react.get('emoji', {}).get('name', '')
                    count = react.get('count', 1)
                    # Add reaction for each count
                    for _ in range(count):
                        reactions.append(Reaction(
                            user='unknown',
                            emoji=emoji
                        ))

                # Create message
                from ..models import Message, MessageType
                msg = Message(
                    id=msg_data.get('id', f'discord_{len(messages)}'),
                    timestamp=timestamp,
                    sender=display_name,
                    content=content,
                    type=MessageType.MEDIA if attachments else MessageType.TEXT,
                    platform='Discord',
                    attachments=attachments,
                    reactions=reactions
                )

                messages.append(msg)
                participants_set.add(display_name)

            except Exception as e:
                self.logger.warning(f"Skipping Discord message: {e}")
                continue

        if not messages:
            raise ValueError("No valid messages found in Discord export")

        # Create participants
        from ..models import Participant
        participants = [
            Participant(id=str(i), username=username)
            for i, username in enumerate(sorted(participants_set))
        ]

        # Create conversation
        from ..models import Conversation
        conversation = Conversation(
            id=Path(file_path).stem,
            title=title,
            messages=messages,
            participants=participants,
            platform='Discord',
            conversation_type='channel',
        )

        conversation.sort_messages()

        self.logger.info(f"Parsed {len(messages)} Discord messages from {len(participants)} participants")

        return conversation

    def _parse_slack(self, data: Dict[str, Any], file_path: str) -> Conversation:
        """
        Parse Slack JSON export format.

        Slack exports can be:
        1. Array of messages: [{"type": "message", "user": "...", "text": "...", "ts": "..."}]
        2. Object with messages: {"ok": true, "messages": [...]}
        """
        # Extract messages array
        if isinstance(data, list):
            messages_data = data
        elif 'messages' in data:
            messages_data = data['messages']
        else:
            raise ValueError("Invalid Slack export format")

        if not messages_data:
            raise ValueError("No messages found in Slack export")

        # Parse messages
        messages = []
        participants_set = set()

        for msg_data in messages_data:
            try:
                # Only process regular messages
                if msg_data.get('type') != 'message':
                    continue

                # Skip bot messages, joins, etc.
                if msg_data.get('subtype') in ['channel_join', 'channel_leave', 'bot_message']:
                    continue

                # Extract user
                user_id = msg_data.get('user', 'Unknown')
                username = msg_data.get('username', user_id)

                # Parse timestamp (Slack uses Unix timestamps with microseconds)
                ts = msg_data.get('ts', '0')
                try:
                    timestamp = datetime.fromtimestamp(float(ts))
                except:
                    timestamp = datetime.now()

                # Get text content
                content = msg_data.get('text', '')

                # Handle attachments
                attachments = []
                for att in msg_data.get('files', []):
                    from ..models import Attachment
                    attachments.append(Attachment(
                        file_path=att.get('url_private', ''),
                        file_type=att.get('mimetype', 'unknown'),
                        file_size=att.get('size', 0)
                    ))

                # Handle reactions
                reactions = []
                for react in msg_data.get('reactions', []):
                    from ..models import Reaction
                    emoji = react.get('name', '')
                    count = react.get('count', 1)
                    users = react.get('users', [])
                    # Add reaction for each user
                    for user in users[:count]:
                        reactions.append(Reaction(
                            user=user,
                            emoji=emoji
                        ))

                # Handle thread replies
                reply_to = None
                if 'thread_ts' in msg_data and msg_data.get('thread_ts') != ts:
                    reply_to = msg_data['thread_ts']

                # Create message
                from ..models import Message, MessageType
                msg = Message(
                    id=ts,
                    timestamp=timestamp,
                    sender=username,
                    content=content,
                    type=MessageType.MEDIA if attachments else MessageType.TEXT,
                    platform='Slack',
                    attachments=attachments,
                    reactions=reactions,
                    reply_to=reply_to
                )

                messages.append(msg)
                participants_set.add(username)

            except Exception as e:
                self.logger.warning(f"Skipping Slack message: {e}")
                continue

        if not messages:
            raise ValueError("No valid messages found in Slack export")

        # Create participants
        from ..models import Participant
        participants = [
            Participant(id=str(i), username=username)
            for i, username in enumerate(sorted(participants_set))
        ]

        # Create conversation
        from ..models import Conversation
        conversation = Conversation(
            id=Path(file_path).stem,
            title=Path(file_path).stem.replace('_', ' ').replace('-', ' ').title(),
            messages=messages,
            participants=participants,
            platform='Slack',
            conversation_type='channel',
        )

        conversation.sort_messages()

        self.logger.info(f"Parsed {len(messages)} Slack messages from {len(participants)} participants")

        return conversation

    def _parse_telegram(self, data: Dict[str, Any], file_path: str) -> Conversation:
        """
        Parse Telegram JSON export format.

        Telegram exports have this structure:
        {
          "name": "Chat Name",
          "type": "personal_chat" | "group" | "supergroup",
          "id": 123456,
          "messages": [
            {
              "id": 1,
              "type": "message",
              "date": "2024-01-01T12:00:00",
              "from": "User Name",
              "from_id": "user123",
              "text": "Hello" or [{"type": "plain", "text": "..."}],
              "photo": "...",
              "file": "..."
            }
          ]
        }
        """
        # Extract metadata
        chat_name = data.get('name', 'Telegram Chat')
        chat_type = data.get('type', 'unknown')

        messages_data = data.get('messages', [])

        if not messages_data:
            raise ValueError("No messages found in Telegram export")

        # Parse messages
        messages = []
        participants_set = set()

        for msg_data in messages_data:
            try:
                # Only process regular messages
                if msg_data.get('type') != 'message':
                    continue

                # Extract sender
                sender = msg_data.get('from', 'Unknown')
                sender_id = msg_data.get('from_id', '')

                # Parse timestamp
                date_str = msg_data.get('date', '')
                timestamp = self._parse_timestamp(date_str)

                # Get text content (can be string or array of text objects)
                text_data = msg_data.get('text', '')
                if isinstance(text_data, list):
                    # Concatenate text elements
                    content = ''.join([
                        item.get('text', '') if isinstance(item, dict) else str(item)
                        for item in text_data
                    ])
                else:
                    content = str(text_data)

                # Handle media
                attachments = []
                if 'photo' in msg_data:
                    from ..models import Attachment
                    attachments.append(Attachment(
                        file_path=msg_data.get('photo', ''),
                        file_type='image',
                        file_size=0
                    ))
                if 'file' in msg_data:
                    from ..models import Attachment
                    file_path = msg_data.get('file', '')
                    mime_type = msg_data.get('mime_type', 'unknown')
                    attachments.append(Attachment(
                        file_path=file_path,
                        file_type=mime_type,
                        file_size=0
                    ))

                # Handle replies
                reply_to = None
                if 'reply_to_message_id' in msg_data:
                    reply_to = str(msg_data['reply_to_message_id'])

                # Create message
                from ..models import Message, MessageType
                msg = Message(
                    id=str(msg_data.get('id', len(messages))),
                    timestamp=timestamp,
                    sender=sender,
                    content=content,
                    type=MessageType.MEDIA if attachments else MessageType.TEXT,
                    platform='Telegram',
                    attachments=attachments,
                    reply_to=reply_to
                )

                messages.append(msg)
                participants_set.add(sender)

            except Exception as e:
                self.logger.warning(f"Skipping Telegram message: {e}")
                continue

        if not messages:
            raise ValueError("No valid messages found in Telegram export")

        # Create participants
        from ..models import Participant
        participants = [
            Participant(id=str(i), username=username)
            for i, username in enumerate(sorted(participants_set))
        ]

        # Create conversation
        from ..models import Conversation
        conversation = Conversation(
            id=Path(file_path).stem,
            title=chat_name,
            messages=messages,
            participants=participants,
            platform='Telegram',
            conversation_type=chat_type,
        )

        conversation.sort_messages()

        self.logger.info(f"Parsed {len(messages)} Telegram messages from {len(participants)} participants")

        return conversation

    def _parse_generic(self, data: Any, file_path: str) -> Conversation:
        """
        Parse generic JSON format.

        Expected structure:
        {
            "messages": [
                {"timestamp": "...", "sender": "...", "content": "..."},
                ...
            ]
        }
        or
        [
            {"timestamp": "...", "sender": "...", "content": "..."},
            ...
        ]
        """
        # Extract messages array
        if isinstance(data, list):
            messages_data = data
        elif isinstance(data, dict) and 'messages' in data:
            messages_data = data['messages']
        else:
            raise ValueError("JSON must be array of messages or object with 'messages' key")

        if not messages_data:
            raise ValueError("No messages found in JSON")

        # Parse messages
        messages = []
        participants_set = set()

        for idx, msg_data in enumerate(messages_data):
            try:
                msg = self._parse_message(msg_data, idx)
                messages.append(msg)
                participants_set.add(msg.sender)
            except Exception as e:
                self.logger.warning(f"Skipping message {idx}: {e}")
                continue

        if not messages:
            raise ValueError("No valid messages found in JSON")

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
            platform='JSON',
            conversation_type='unknown',
        )

        conversation.sort_messages()

        self.logger.info(f"Parsed {len(messages)} messages from {len(participants)} participants")

        return conversation

    def _parse_message(self, data: Dict[str, Any], index: int) -> Message:
        """
        Parse a message from generic JSON.

        Args:
            data: Message data dict
            index: Message index

        Returns:
            Message object
        """
        # Extract fields with common variations
        sender = (data.get('sender') or data.get('username') or
                 data.get('user') or data.get('author') or 'Unknown')

        content = (data.get('content') or data.get('message') or
                  data.get('text') or data.get('body') or '')

        # Parse timestamp
        timestamp_str = (data.get('timestamp') or data.get('time') or
                        data.get('date') or data.get('created_at'))

        if timestamp_str:
            timestamp = self._parse_timestamp(str(timestamp_str))
        else:
            # Fallback to sequential timestamps
            from datetime import timedelta
            timestamp = datetime(2024, 1, 1, 0, 0, 0) + timedelta(minutes=index)

        return Message(
            id=data.get('id', f'json_{index}'),
            timestamp=timestamp,
            sender=str(sender),
            content=str(content),
            type=MessageType.TEXT,
            platform='JSON',
        )

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp with various format support."""
        # Try ISO format first
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            pass

        # Common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # Unix timestamp
        try:
            return datetime.fromtimestamp(float(timestamp_str))
        except:
            pass

        raise ValueError(f"Could not parse timestamp: {timestamp_str}")
