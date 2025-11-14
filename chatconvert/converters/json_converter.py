"""
JSON Converter.

Converts conversations to structured JSON format with optional analytics.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List

from .base_converter import BaseConverter
from ..models import Conversation, ConversionResult, Message


class JSONConverter(BaseConverter):
    """Convert conversations to JSON format."""

    def get_file_extension(self) -> str:
        return 'json'

    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert conversation to JSON.

        Config options:
        - pretty: Pretty print JSON (default: True)
        - include_analytics: Include analytics data (default: False)
        - include_metadata: Include message metadata (default: True)
        - compact: Minimal JSON (exclude optional fields) (default: False)

        Args:
            conversation: Conversation to convert
            output_file: Path to output .json file

        Returns:
            ConversionResult
        """
        start_time = time.time()
        path = self._validate_output_path(output_file)

        try:
            # Get config
            pretty = self.config.get('pretty', True)
            include_analytics = self.config.get('include_analytics', False)
            include_metadata = self.config.get('include_metadata', True)
            compact = self.config.get('compact', False)

            # Build JSON structure
            data = {
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'platform': conversation.platform,
                    'type': conversation.conversation_type,
                }
            }

            # Add participants
            if conversation.participants and not compact:
                data['participants'] = [
                    {
                        'id': p.id,
                        'username': p.username,
                        'display_name': p.display_name,
                        'role': p.role,
                    }
                    for p in conversation.participants
                ]
            else:
                data['participants'] = conversation.get_participants_list()

            # Add messages
            data['messages'] = [
                self._message_to_dict(msg, include_metadata, compact)
                for msg in conversation.messages
            ]

            # Add statistics
            data['statistics'] = self._calculate_statistics(conversation)

            # Add analytics if requested
            if include_analytics:
                data['analytics'] = self._generate_analytics(conversation)

            # Add metadata
            if include_metadata and not compact:
                data['metadata'] = {
                    'message_count': len(conversation.messages),
                    'participant_count': len(conversation.get_participants_list()),
                    'date_range': {
                        'start': conversation.get_date_range()[0].isoformat() if conversation.get_date_range()[0] else None,
                        'end': conversation.get_date_range()[1].isoformat() if conversation.get_date_range()[1] else None,
                    },
                    'export_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'format_version': '2.0',
                }

            # Write JSON
            json_str = json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)
            self._write_file(path, json_str)

            processing_time = time.time() - start_time

            return self._create_result(
                success=True,
                output_file=str(path),
                message_count=len(conversation.messages),
                processing_time=processing_time,
                statistics={
                    'file_size_bytes': len(json_str.encode('utf-8')),
                    'pretty': pretty,
                    'includes_analytics': include_analytics,
                }
            )

        except Exception as e:
            self.logger.error(f"JSON conversion failed: {e}")
            return self._create_result(
                success=False,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _message_to_dict(self, msg: Message, include_metadata: bool, compact: bool) -> Dict[str, Any]:
        """Convert Message object to dictionary."""
        data = {
            'id': msg.id,
            'timestamp': msg.timestamp.isoformat(),
            'sender': msg.sender,
            'content': msg.content,
        }

        if not compact:
            data['type'] = msg.type.value

            if msg.reply_to:
                data['reply_to'] = msg.reply_to

            if msg.edited:
                data['edited'] = True
                if msg.edited_timestamp:
                    data['edited_timestamp'] = msg.edited_timestamp.isoformat()

            if msg.deleted:
                data['deleted'] = True

            if msg.attachments:
                data['attachments'] = [
                    {
                        'type': att.type.value,
                        'filename': att.filename,
                        'url': att.url,
                        'size': att.size_bytes,
                    }
                    for att in msg.attachments
                ]

            if msg.reactions:
                data['reactions'] = [
                    {
                        'type': react.type.value,
                        'user': react.user,
                        'emoji': react.emoji,
                    }
                    for react in msg.reactions
                ]

            if msg.mentions:
                data['mentions'] = msg.mentions

            if include_metadata and msg.platform:
                data['platform'] = msg.platform

            if include_metadata and msg.sentiment_score is not None:
                data['sentiment'] = {
                    'score': msg.sentiment_score,
                    'label': msg.sentiment_label,
                }

        return data

    def _calculate_statistics(self, conversation: Conversation) -> Dict[str, Any]:
        """Calculate conversation statistics."""
        messages = conversation.messages

        # Count by user
        user_counts = {}
        for msg in messages:
            user_counts[msg.sender] = user_counts.get(msg.sender, 0) + 1

        # Count by date
        date_counts = {}
        for msg in messages:
            date_key = msg.timestamp.strftime('%Y-%m-%d')
            date_counts[date_key] = date_counts.get(date_key, 0) + 1

        return {
            'total_messages': len(messages),
            'total_participants': len(conversation.get_participants_list()),
            'messages_by_user': user_counts,
            'messages_by_date': date_counts,
            'average_message_length': sum(len(m.content) for m in messages) / len(messages) if messages else 0,
        }

    def _generate_analytics(self, conversation: Conversation) -> Dict[str, Any]:
        """Generate analytics data for Chart.js compatibility."""
        messages = conversation.messages

        # Timeline data
        timeline_labels = []
        timeline_data = []

        # Group by date
        date_counts = {}
        for msg in messages:
            date_key = msg.timestamp.strftime('%Y-%m-%d')
            date_counts[date_key] = date_counts.get(date_key, 0) + 1

        for date_key in sorted(date_counts.keys()):
            timeline_labels.append(date_key)
            timeline_data.append(date_counts[date_key])

        # User activity data
        user_labels = []
        user_data = []

        user_counts = {}
        for msg in messages:
            user_counts[msg.sender] = user_counts.get(msg.sender, 0) + 1

        for user in sorted(user_counts.keys(), key=lambda u: user_counts[u], reverse=True):
            user_labels.append(user)
            user_data.append(user_counts[user])

        return {
            'timeline': {
                'labels': timeline_labels,
                'datasets': [{
                    'label': 'Messages per Day',
                    'data': timeline_data,
                }]
            },
            'user_activity': {
                'labels': user_labels,
                'datasets': [{
                    'label': 'Messages per User',
                    'data': user_data,
                }]
            }
        }
