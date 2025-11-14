"""
CSV Parser - Parse CSV chat logs.

Expected CSV format:
  timestamp,username,message
  2024-01-01 10:00:00,Alice,Hello!
  2024-01-01 10:01:00,Bob,Hi Alice!

Supports flexible column names and date formats.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType


class CSVParser(BaseParser):
    """Parse CSV format chat logs."""

    # Common column name variations
    TIMESTAMP_COLUMNS = ['timestamp', 'time', 'date', 'datetime', 'sent_at', 'created_at']
    USERNAME_COLUMNS = ['username', 'user', 'sender', 'from', 'author', 'name']
    MESSAGE_COLUMNS = ['message', 'content', 'text', 'body']

    def can_parse(self, file_path: str) -> bool:
        """Check if file is CSV format."""
        ext = self._get_file_extension(file_path)
        if ext != 'csv':
            return False

        # Try to read first line to verify CSV format
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                csv.Sniffer().sniff(f.read(1024))
            return True
        except:
            return False

    def parse(self, file_path: str) -> Conversation:
        """
        Parse CSV file into Conversation object.

        Args:
            file_path: Path to CSV file

        Returns:
            Conversation object

        Raises:
            ValueError: If CSV format is invalid
            FileNotFoundError: If file doesn't exist
        """
        self._validate_file(file_path)

        self.logger.info(f"Parsing CSV file: {file_path}")

        try:
            # Read CSV
            content = self._read_file(file_path)
            rows = list(csv.DictReader(content.splitlines()))

            if not rows:
                raise ValueError("CSV file is empty")

            # Detect column mapping
            column_map = self._detect_columns(rows[0].keys())
            self.logger.info(f"Detected columns: {column_map}")

            # Parse messages
            messages = []
            participants_set = set()

            for row_num, row in enumerate(rows, 1):
                try:
                    msg = self._parse_message(row, column_map, row_num)
                    messages.append(msg)
                    participants_set.add(msg.sender)
                except Exception as e:
                    self.logger.warning(f"Skipping row {row_num}: {e}")
                    continue

            if not messages:
                raise ValueError("No valid messages found in CSV")

            # Create participants list
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
                platform='CSV',
                conversation_type='unknown',
            )

            conversation.sort_messages()

            self.logger.info(f"Parsed {len(messages)} messages from {len(participants)} participants")

            return conversation

        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")
        except Exception as e:
            self.logger.error(f"CSV parsing failed: {e}")
            raise

    def _detect_columns(self, headers: List[str]) -> Dict[str, str]:
        """
        Detect which columns contain timestamp, username, and message.

        Args:
            headers: CSV column headers

        Returns:
            Dict mapping 'timestamp', 'username', 'message' to actual column names

        Raises:
            ValueError: If required columns cannot be detected
        """
        # Convert to list if dict_keys
        headers = list(headers)
        headers_lower = [h.lower().strip() for h in headers]
        mapping = {}

        # Find timestamp column
        for col in self.TIMESTAMP_COLUMNS:
            if col in headers_lower:
                mapping['timestamp'] = headers[headers_lower.index(col)]
                break

        # Find username column
        for col in self.USERNAME_COLUMNS:
            if col in headers_lower:
                mapping['username'] = headers[headers_lower.index(col)]
                break

        # Find message column
        for col in self.MESSAGE_COLUMNS:
            if col in headers_lower:
                mapping['message'] = headers[headers_lower.index(col)]
                break

        # Validate required columns found
        if 'username' not in mapping:
            raise ValueError(f"Could not find username column in: {headers}")

        if 'message' not in mapping:
            raise ValueError(f"Could not find message column in: {headers}")

        # Timestamp is optional - will use row number if missing
        if 'timestamp' not in mapping:
            self.logger.warning("No timestamp column found, using sequential timestamps")

        return mapping

    def _parse_message(
        self,
        row: Dict[str, str],
        column_map: Dict[str, str],
        row_num: int
    ) -> Message:
        """
        Parse a CSV row into a Message object.

        Args:
            row: CSV row as dict
            column_map: Column name mapping
            row_num: Row number (for ID and fallback timestamp)

        Returns:
            Message object
        """
        # Extract fields
        username = row[column_map['username']].strip()
        content = row[column_map['message']].strip()

        # Parse timestamp
        if 'timestamp' in column_map:
            timestamp_str = row[column_map['timestamp']].strip()
            timestamp = self._parse_timestamp(timestamp_str)
        else:
            # Use sequential timestamps (1 minute apart)
            timestamp = datetime(2024, 1, 1, 0, 0, 0) + timedelta(minutes=row_num)

        # Create message
        return Message(
            id=f"csv_{row_num}",
            timestamp=timestamp,
            sender=username,
            content=content,
            type=MessageType.TEXT,
            platform='CSV',
        )

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse timestamp string with various format support.

        Args:
            timestamp_str: Timestamp string

        Returns:
            datetime object

        Raises:
            ValueError: If timestamp cannot be parsed
        """
        # Common timestamp formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # Try ISO format parsing
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            pass

        raise ValueError(f"Could not parse timestamp: {timestamp_str}")