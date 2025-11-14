"""
Facebook Messenger Parser - Parse Facebook Messenger JSON exports.

Supports Facebook data download format (JSON).
Facebook provides chat history in JSON format when you download your data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType, Attachment


class MessengerParser(BaseParser):
    """Parse Facebook Messenger JSON exports."""

    def can_parse(self, file_path: str) -> bool:
        """Check if file is Facebook Messenger export."""
        ext = self._get_file_extension(file_path)
        if ext != 'json':
            return False

        try:
            content = self._read_file(file_path)
            data = json.loads(content)

            # Facebook Messenger exports have specific structure
            if isinstance(data, dict):
                # Check for Messenger-specific fields
                if 'participants' in data and 'messages' in data:
                    # Check if messages have sender_name field (Messenger-specific)
                    if data['messages'] and 'sender_name' in data['messages'][0]:
                        return True

            return False
        except:
            return False

    def parse(self, file_path: str) -> Conversation:
        """
        Parse Facebook Messenger JSON export.

        Facebook Messenger exports have this structure:
        {
          "participants": [
            {"name": "User Name"},
            ...
          ],
          "messages": [
            {
              "sender_name": "User Name",
              "timestamp_ms": 1234567890123,
              "content": "Message text",
              "photos": [...],
              "videos": [...],
              "files": [...],
              "reactions": [...]
            }
          ],
          "title": "Chat Title",
          "is_still_participant": true,
          "thread_path": "inbox/username_id"
        }

        Args:
            file_path: Path to Messenger JSON file

        Returns:
            Conversation object

        Raises:
            ValueError: If format is invalid
            FileNotFoundError: If file doesn't exist
        """
        self._validate_file(file_path)
        self.logger.info(f"Parsing Facebook Messenger file: {file_path}")

        try:
            content = self._read_file(file_path)
            data = json.loads(content)

            # Extract metadata
            title = data.get('title', 'Messenger Chat')
            participant_names = [p.get('name', 'Unknown') for p in data.get('participants', [])]

            messages_data = data.get('messages', [])

            if not messages_data:
                raise ValueError("No messages found in Messenger export")

            # Parse messages
            messages = []
            participants_set = set()

            for msg_data in messages_data:
                try:
                    # Extract sender
                    sender = msg_data.get('sender_name', 'Unknown')

                    # Parse timestamp (milliseconds)
                    timestamp_ms = msg_data.get('timestamp_ms', 0)
                    timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0)

                    # Get content
                    content = msg_data.get('content', '')

                    # Handle photos
                    attachments = []
                    for photo in msg_data.get('photos', []):
                        attachments.append(Attachment(
                            file_path=photo.get('uri', ''),
                            file_type='image',
                            file_size=0
                        ))

                    # Handle videos
                    for video in msg_data.get('videos', []):
                        attachments.append(Attachment(
                            file_path=video.get('uri', ''),
                            file_type='video',
                            file_size=0
                        ))

                    # Handle files
                    for file in msg_data.get('files', []):
                        attachments.append(Attachment(
                            file_path=file.get('uri', ''),
                            file_type='file',
                            file_size=0
                        ))

                    # Handle audio files
                    for audio in msg_data.get('audio_files', []):
                        attachments.append(Attachment(
                            file_path=audio.get('uri', ''),
                            file_type='audio',
                            file_size=0
                        ))

                    # Handle reactions
                    reactions = []
                    for reaction in msg_data.get('reactions', []):
                        from ..models import Reaction
                        reactions.append(Reaction(
                            user=reaction.get('actor', 'Unknown'),
                            emoji=reaction.get('reaction', '❤️')
                        ))

                    # Determine message type
                    if attachments:
                        msg_type = MessageType.MEDIA
                    elif msg_data.get('call_duration'):
                        msg_type = MessageType.SYSTEM
                        if not content:
                            content = f"Call duration: {msg_data['call_duration']} seconds"
                    else:
                        msg_type = MessageType.TEXT

                    # Create message
                    msg = Message(
                        id=f"messenger_{timestamp_ms}",
                        timestamp=timestamp,
                        sender=sender,
                        content=content,
                        type=msg_type,
                        platform='Messenger',
                        attachments=attachments,
                        reactions=reactions
                    )

                    messages.append(msg)
                    participants_set.add(sender)

                except Exception as e:
                    self.logger.warning(f"Skipping Messenger message: {e}")
                    continue

            if not messages:
                raise ValueError("No valid messages found in Messenger export")

            # Create participants (use participant_names if available)
            if participant_names:
                participants = [
                    Participant(id=str(i), username=name)
                    for i, name in enumerate(participant_names)
                ]
            else:
                participants = [
                    Participant(id=str(i), username=username)
                    for i, username in enumerate(sorted(participants_set))
                ]

            # Create conversation
            conversation = Conversation(
                id=Path(file_path).stem,
                title=title,
                messages=messages,
                participants=participants,
                platform='Messenger',
                conversation_type='chat',
            )

            conversation.sort_messages()

            self.logger.info(f"Parsed {len(messages)} Messenger messages from {len(participants)} participants")

            return conversation

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Messenger JSON: {e}")
        except Exception as e:
            self.logger.error(f"Messenger parsing failed: {e}")
            raise
