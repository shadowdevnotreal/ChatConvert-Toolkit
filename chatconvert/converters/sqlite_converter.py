"""
SQLite Converter - Create relational database from conversations.

Features:
- Normalized schema with messages and participants tables
- Statistics views
- Indexes for performance
- Full-text search support (FTS5)
- Query-ready structure
"""

import sqlite3
import time
from pathlib import Path

from .base_converter import BaseConverter
from ..models import Conversation, ConversionResult


class SQLiteConverter(BaseConverter):
    """Convert conversations to SQLite database format."""

    def get_file_extension(self) -> str:
        return 'db'

    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert conversation to SQLite database.

        Config options:
        - enable_fts: Enable full-text search (default: False)
        - create_views: Create statistics views (default: True)
        - create_indexes: Create performance indexes (default: True)

        Args:
            conversation: Conversation to convert
            output_file: Path to output .db file

        Returns:
            ConversionResult
        """
        start_time = time.time()
        path = self._validate_output_path(output_file)

        # Remove existing database
        if path.exists():
            path.unlink()

        try:
            # Get config
            enable_fts = self.config.get('enable_fts', False)
            create_views = self.config.get('create_views', True)
            create_indexes = self.config.get('create_indexes', True)

            # Create database
            with sqlite3.connect(str(path)) as conn:
                cursor = conn.cursor()

                # Create schema
                self._create_schema(cursor)

                if create_indexes:
                    self._create_indexes(cursor)

                if create_views:
                    self._create_views(cursor)

                if enable_fts:
                    self._create_fts(cursor)

                # Insert data
                self._insert_conversation(cursor, conversation)
                self._insert_participants(cursor, conversation)
                self._insert_messages(cursor, conversation)

                conn.commit()

            processing_time = time.time() - start_time

            return self._create_result(
                success=True,
                output_file=str(path),
                message_count=len(conversation.messages),
                processing_time=processing_time,
                statistics={
                    'participants': len(conversation.get_participants_list()),
                    'fts_enabled': enable_fts,
                }
            )

        except Exception as e:
            self.logger.error(f"SQLite conversion failed: {e}")
            return self._create_result(
                success=False,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _create_schema(self, cursor: sqlite3.Cursor):
        """Create database schema."""

        # Conversation metadata table
        cursor.execute('''
            CREATE TABLE conversation (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                platform TEXT,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Participants table
        cursor.execute('''
            CREATE TABLE participants (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                display_name TEXT,
                role TEXT
            )
        ''')

        # Messages table
        cursor.execute('''
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT DEFAULT 'text',
                platform TEXT,
                reply_to TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversation(id),
                FOREIGN KEY (sender) REFERENCES participants(username)
            )
        ''')

        # Attachments table
        cursor.execute('''
            CREATE TABLE attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                file_path TEXT,
                file_type TEXT,
                file_size INTEGER,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')

        # Reactions table
        cursor.execute('''
            CREATE TABLE reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                user TEXT,
                emoji TEXT,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')

    def _create_indexes(self, cursor: sqlite3.Cursor):
        """Create performance indexes."""

        cursor.execute('CREATE INDEX idx_messages_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX idx_messages_sender ON messages(sender)')
        cursor.execute('CREATE INDEX idx_messages_conversation ON messages(conversation_id)')

    def _create_views(self, cursor: sqlite3.Cursor):
        """Create statistics views."""

        # Per-participant statistics
        cursor.execute('''
            CREATE VIEW participant_stats AS
            SELECT
                p.username,
                p.display_name,
                COUNT(m.id) as message_count,
                MIN(m.timestamp) as first_message,
                MAX(m.timestamp) as last_message
            FROM participants p
            LEFT JOIN messages m ON p.username = m.sender
            GROUP BY p.username, p.display_name
            ORDER BY message_count DESC
        ''')

        # Daily activity
        cursor.execute('''
            CREATE VIEW daily_activity AS
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as message_count,
                COUNT(DISTINCT sender) as active_participants
            FROM messages
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''')

        # Hourly activity
        cursor.execute('''
            CREATE VIEW hourly_activity AS
            SELECT
                strftime('%H', timestamp) as hour,
                COUNT(*) as message_count
            FROM messages
            GROUP BY hour
            ORDER BY hour
        ''')

    def _create_fts(self, cursor: sqlite3.Cursor):
        """Create full-text search table."""

        cursor.execute('''
            CREATE VIRTUAL TABLE messages_fts USING fts5(
                message_id,
                sender,
                content,
                timestamp
            )
        ''')

    def _insert_conversation(self, cursor: sqlite3.Cursor, conversation: Conversation):
        """Insert conversation metadata."""

        cursor.execute('''
            INSERT INTO conversation (id, title, platform, type)
            VALUES (?, ?, ?, ?)
        ''', (
            conversation.id,
            conversation.title,
            conversation.platform,
            conversation.conversation_type
        ))

    def _insert_participants(self, cursor: sqlite3.Cursor, conversation: Conversation):
        """Insert participants."""

        for participant in conversation.participants:
            cursor.execute('''
                INSERT INTO participants (id, username, display_name, role)
                VALUES (?, ?, ?, ?)
            ''', (
                participant.id,
                participant.username,
                participant.display_name,
                participant.role
            ))

    def _insert_messages(self, cursor: sqlite3.Cursor, conversation: Conversation):
        """Insert messages and related data."""

        for msg in conversation.messages:
            # Insert message
            cursor.execute('''
                INSERT INTO messages (
                    id, conversation_id, timestamp, sender,
                    content, type, platform, reply_to
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                msg.id,
                conversation.id,
                msg.timestamp.isoformat(),
                msg.sender,
                msg.content,
                msg.type.value,
                msg.platform,
                msg.reply_to
            ))

            # Insert FTS data if enabled
            if cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages_fts'").fetchone():
                cursor.execute('''
                    INSERT INTO messages_fts (message_id, sender, content, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    msg.id,
                    msg.sender,
                    msg.content,
                    msg.timestamp.isoformat()
                ))

            # Insert attachments
            for attachment in msg.attachments:
                cursor.execute('''
                    INSERT INTO attachments (message_id, file_path, file_type, file_size)
                    VALUES (?, ?, ?, ?)
                ''', (
                    msg.id,
                    attachment.file_path,
                    attachment.file_type,
                    attachment.file_size
                ))

            # Insert reactions
            for reaction in msg.reactions:
                cursor.execute('''
                    INSERT INTO reactions (message_id, user, emoji)
                    VALUES (?, ?, ?)
                ''', (
                    msg.id,
                    reaction.user,
                    reaction.emoji
                ))
