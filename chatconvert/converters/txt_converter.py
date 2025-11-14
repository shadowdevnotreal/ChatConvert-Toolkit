"""
Plain Text (TXT) Converter.

Converts conversations to plain text format with various styles.
"""

import time
from pathlib import Path
from typing import List

from .base_converter import BaseConverter
from ..models import Conversation, ConversionResult, Message


class TXTConverter(BaseConverter):
    """Convert conversations to plain text format."""

    # Available text styles
    STYLES = {
        'simple': 'Simple format with minimal decoration',
        'irc': 'IRC-style chat format',
        'timestamp': 'Full timestamp format',
        'clean': 'Clean format without timestamps',
    }

    def get_file_extension(self) -> str:
        return 'txt'

    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert conversation to plain text.

        Config options:
        - style: 'simple', 'irc', 'timestamp', or 'clean' (default: 'simple')
        - include_stats: Include statistics footer (default: True)
        - wrap_width: Line wrap width (default: 80, 0 = no wrap)

        Args:
            conversation: Conversation to convert
            output_file: Path to output .txt file

        Returns:
            ConversionResult
        """
        start_time = time.time()
        path = self._validate_output_path(output_file)

        try:
            # Get config
            style = self.config.get('style', 'simple')
            include_stats = self.config.get('include_stats', True)
            wrap_width = self.config.get('wrap_width', 80)

            # Generate content
            lines = []

            # Header
            lines.append("=" * 60)
            lines.append(conversation.title.center(60))
            lines.append("=" * 60)
            lines.append("")

            # Convert based on style
            if style == 'irc':
                lines.extend(self._format_irc(conversation))
            elif style == 'timestamp':
                lines.extend(self._format_timestamp(conversation))
            elif style == 'clean':
                lines.extend(self._format_clean(conversation))
            else:  # simple
                lines.extend(self._format_simple(conversation))

            # Statistics footer
            if include_stats:
                lines.append("")
                lines.append("=" * 60)
                lines.append("Statistics")
                lines.append("=" * 60)
                lines.append(f"Total Messages: {len(conversation.messages)}")
                lines.append(f"Participants: {len(conversation.get_participants_list())}")

                date_range = conversation.get_date_range()
                if date_range[0]:
                    lines.append(f"Period: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")

            # Join and write
            content = "\n".join(lines)

            # Word wrap if needed
            if wrap_width > 0:
                content = self._wrap_text(content, wrap_width)

            self._write_file(path, content)

            processing_time = time.time() - start_time

            return self._create_result(
                success=True,
                output_file=str(path),
                message_count=len(conversation.messages),
                processing_time=processing_time,
                statistics={
                    'style': style,
                    'participants': len(conversation.get_participants_list()),
                }
            )

        except Exception as e:
            self.logger.error(f"TXT conversion failed: {e}")
            return self._create_result(
                success=False,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _format_simple(self, conversation: Conversation) -> List[str]:
        """Simple format with timestamps."""
        lines = []

        for msg in conversation.messages:
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            lines.append(f"[{timestamp}] {msg.sender}")
            lines.append(f"  {msg.content}")
            lines.append("")

        return lines

    def _format_irc(self, conversation: Conversation) -> List[str]:
        """IRC-style chat format."""
        lines = []

        for msg in conversation.messages:
            timestamp = msg.timestamp.strftime('%H:%M')
            lines.append(f"[{timestamp}] <{msg.sender}> {msg.content}")

        return lines

    def _format_timestamp(self, conversation: Conversation) -> List[str]:
        """Full timestamp format."""
        lines = []

        for msg in conversation.messages:
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            lines.append(f"{timestamp} | {msg.sender}")
            lines.append(f"{' ' * (len(timestamp) + 3)}| {msg.content}")
            lines.append("")

        return lines

    def _format_clean(self, conversation: Conversation) -> List[str]:
        """Clean format without timestamps."""
        lines = []
        current_sender = None

        for msg in conversation.messages:
            # Add sender name if changed
            if msg.sender != current_sender:
                if current_sender is not None:
                    lines.append("")
                lines.append(f"{msg.sender}:")
                current_sender = msg.sender

            lines.append(f"  {msg.content}")

        return lines

    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width."""
        lines = text.split('\n')
        wrapped_lines = []

        for line in lines:
            if len(line) <= width or line.startswith(' ' * 4):  # Don't wrap indented
                wrapped_lines.append(line)
            else:
                # Simple word wrap
                words = line.split()
                current_line = []
                current_length = 0

                for word in words:
                    word_length = len(word) + 1

                    if current_length + word_length > width:
                        wrapped_lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = word_length
                    else:
                        current_line.append(word)
                        current_length += word_length

                if current_line:
                    wrapped_lines.append(' '.join(current_line))

        return '\n'.join(wrapped_lines)
