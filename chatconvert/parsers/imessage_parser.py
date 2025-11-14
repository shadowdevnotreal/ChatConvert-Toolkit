"""
iMessage Parser - Parse iMessage exports from macOS/iOS.

Supports:
- iMessage SQLite database (chat.db from ~/Library/Messages/)
- iMessage text exports
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class iMessageParser(BaseParser):
    """Parse iMessage database exports."""

    def can_parse(self, file_path: str) -> bool:
        """Check if file is iMessage database."""
        ext = self._get_file_extension(file_path)

        if ext in ['db', 'sqlite']:
            try:
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                # Check for iMessage-specific tables
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND (name='message' OR name='chat')
                """)
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()

                # iMessage databases have both message and chat tables
                return 'message' in tables and 'chat' in tables
            except:
                pass

        return False

    def parse(self, file_path: str) -> Conversation:
        """
        Parse iMessage database.

        Args:
            file_path: Path to chat.db file

        Returns:
            Conversation object

        Raises:
            ValueError: If database is invalid
            FileNotFoundError: If file doesn't exist
        """
        self._validate_file(file_path)
        self.logger.info(f"Parsing iMessage database: {file_path}")

        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # Get chat information
            cursor.execute("""
                SELECT
                    chat_id,
                    display_name,
                    chat_identifier
                FROM chat
                LIMIT 1
            """)

            chat_row = cursor.fetchone()
            if chat_row:
                chat_id, display_name, chat_identifier = chat_row
                title = display_name or chat_identifier or "iMessage Chat"
            else:
                title = "iMessage Chat"

            # Get handles (participants)
            cursor.execute("""
                SELECT
                    ROWID,
                    id
                FROM handle
            """)
            handles = {row[0]: row[1] for row in cursor.fetchall()}

            # Get messages
            cursor.execute("""
                SELECT
                    m.ROWID,
                    m.text,
                    m.date,
                    m.is_from_me,
                    m.handle_id,
                    m.cache_has_attachments
                FROM message m
                ORDER BY m.date
            """)

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                raise ValueError("No messages found in iMessage database")

            messages = []
            participants_set = set()

            for row in rows:
                try:
                    msg_id, text, date_val, is_from_me, handle_id, has_attachments = row

                    # Skip empty messages
                    if not text:
                        continue

                    # macOS/iOS stores dates as nanoseconds since 2001-01-01
                    # Convert to Unix timestamp
                    ios_epoch = datetime(2001, 1, 1)
                    if date_val:
                        # date_val is in nanoseconds, convert to seconds
                        timestamp = ios_epoch + timedelta(seconds=date_val / 1_000_000_000)
                    else:
                        timestamp = datetime.now()

                    # Determine sender
                    if is_from_me:
                        sender = 'Me'
                    else:
                        sender = handles.get(handle_id, 'Unknown')

                    # Determine message type
                    msg_type = MessageType.MEDIA if has_attachments else MessageType.TEXT

                    # Create message
                    msg = Message(
                        id=f"imessage_{msg_id}",
                        timestamp=timestamp,
                        sender=sender,
                        content=text,
                        type=msg_type,
                        platform='iMessage',
                    )

                    messages.append(msg)
                    participants_set.add(sender)
                    if sender != 'Me' and handle_id in handles:
                        participants_set.add(handles[handle_id])

                except Exception as e:
                    self.logger.warning(f"Skipping iMessage: {e}")
                    continue

            if not messages:
                raise ValueError("No valid messages found in iMessage database")

            # Create participants
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
                platform='iMessage',
                conversation_type='chat',
            )

            conversation.sort_messages()

            self.logger.info(f"Parsed {len(messages)} iMessages from {len(participants)} participants")

            return conversation

        except sqlite3.Error as e:
            raise ValueError(f"Invalid iMessage database: {e}")
        except Exception as e:
            self.logger.error(f"iMessage parsing failed: {e}")
            raise
