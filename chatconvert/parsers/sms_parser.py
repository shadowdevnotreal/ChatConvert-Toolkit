"""
SMS/MMS Parser - Parse Android and iOS SMS/MMS backups.

Supports:
- Android SMS backup (XML format)
- iOS SMS backup (SQLite database)
- Generic XML exports from apps like SMS Backup & Restore
"""

import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_parser import BaseParser
from ..models import Conversation, Message, Participant, MessageType, Attachment


class SMSParser(BaseParser):
    """Parse SMS/MMS backup files from Android and iOS."""

    def can_parse(self, file_path: str) -> bool:
        """Check if file is SMS backup format or generic phone/message XML."""
        ext = self._get_file_extension(file_path)

        # Accept any valid XML file - will try to parse various formats
        if ext == 'xml':
            try:
                # Just check if it's valid XML, not specific structure
                tree = ET.parse(file_path)
                root = tree.getroot()
                # Accept XML files with common message/call related root elements
                root_tag = root.tag.lower()
                if any(keyword in root_tag for keyword in ['sms', 'message', 'call', 'phone', 'log', 'conversation', 'chat']):
                    return True
                # Also check if it contains common child elements
                content = ET.tostring(root, encoding='unicode').lower()
                if any(tag in content for tag in ['<sms', '<message', '<call', '<text', '<body', '<conversation']):
                    return True
            except:
                pass

        # iOS SMS backups might be in SQLite database
        if ext in ['db', 'sqlite']:
            try:
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                # Check for SMS table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='message'")
                if cursor.fetchone():
                    conn.close()
                    return True
                conn.close()
            except:
                pass

        return False

    def parse(self, file_path: str) -> Conversation:
        """
        Parse SMS/MMS backup file.

        Args:
            file_path: Path to SMS backup file

        Returns:
            Conversation object

        Raises:
            ValueError: If format is invalid
            FileNotFoundError: If file doesn't exist
        """
        self._validate_file(file_path)
        ext = self._get_file_extension(file_path)

        self.logger.info(f"Parsing SMS backup file: {file_path}")

        if ext == 'xml':
            return self._parse_xml(file_path)
        elif ext in ['db', 'sqlite']:
            return self._parse_sqlite(file_path)
        else:
            raise ValueError(f"Unsupported SMS backup format: {ext}")

    def _parse_xml(self, file_path: str) -> Conversation:
        """Parse Android SMS Backup XML format or generic phone log XML."""

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Try to find message elements - support multiple tag names
            sms_elements = root.findall('.//sms')
            mms_elements = root.findall('.//mms')  # MMS messages
            if not sms_elements and not mms_elements:
                sms_elements = root.findall('.//message')
            if not sms_elements and not mms_elements:
                sms_elements = root.findall('.//call')
            if not sms_elements and not mms_elements:
                # Try any child element
                sms_elements = list(root)

            if not sms_elements and not mms_elements:
                raise ValueError("No message elements found in XML")

            messages = []
            participants_set = set()

            # Process MMS messages first (they have media attachments)
            for mms in mms_elements:
                try:
                    msg = self._parse_mms_message(mms)
                    if msg:
                        messages.append(msg)
                        participants_set.add(msg.sender)
                except Exception as e:
                    self.logger.warning(f"Skipping MMS message: {e}")

            for sms in sms_elements:
                try:
                    # Extract attributes - try various common attribute names
                    address = sms.get('address') or sms.get('contact') or sms.get('number') or sms.get('phone') or 'Unknown'
                    body = sms.get('body') or sms.get('text') or sms.get('content') or sms.text or ''

                    # Handle call logs (which don't have body text)
                    duration = sms.get('duration')
                    contact_name = sms.get('contact_name')
                    readable_date = sms.get('readable_date')

                    # Check if this is a call log (has duration attribute)
                    if duration is not None:
                        # This is a call log entry
                        duration_sec = int(duration) if duration else 0

                        # Build descriptive content
                        if duration_sec > 0:
                            mins, secs = divmod(duration_sec, 60)
                            if mins > 0:
                                body = f"📞 Call duration: {mins}m {secs}s"
                            else:
                                body = f"📞 Call duration: {secs}s"
                        else:
                            body = "❌ Missed call"

                        # Add contact name or number
                        if contact_name and contact_name != "(Unknown)":
                            body = f"{body}\nContact: {contact_name}"
                        if address and address != "Unknown":
                            body = f"{body}\nNumber: {address}"

                        # Add readable date if available
                        if readable_date:
                            body = f"{body}\nTime: {readable_date}"

                    # Try various timestamp formats
                    timestamp_ms = sms.get('date') or sms.get('time') or sms.get('timestamp') or '0'
                    msg_type = sms.get('type') or sms.get('direction') or '1'  # 1=received, 2=sent, 3=missed

                    # Parse timestamp (try milliseconds first, then seconds)
                    try:
                        timestamp_val = int(timestamp_ms)
                        # If value is very large, it's likely milliseconds
                        if timestamp_val > 10000000000:
                            timestamp = datetime.fromtimestamp(timestamp_val / 1000.0)
                        else:
                            timestamp = datetime.fromtimestamp(timestamp_val)
                    except:
                        timestamp = datetime.now()

                    # Determine sender - support various type indicators
                    if msg_type in ['2', 'sent', 'outgoing', 'out']:
                        sender = 'Me'
                    else:  # Received message or call
                        # Use contact name if available, otherwise use number
                        if contact_name and contact_name != "(Unknown)":
                            sender = contact_name
                        else:
                            sender = address if address else "Unknown"

                    # Create message
                    msg = Message(
                        id=f"sms_{timestamp_ms}",
                        timestamp=timestamp,
                        sender=sender,
                        content=body if body else "(No content)",
                        type=MessageType.TEXT,
                        platform='SMS/Call Log',
                    )

                    messages.append(msg)
                    participants_set.add(sender)
                    participants_set.add(address)

                except Exception as e:
                    self.logger.warning(f"Skipping SMS message: {e}")
                    continue

            if not messages:
                raise ValueError("No valid messages found in SMS backup")

            # Create participants
            participants = [
                Participant(id=str(i), username=username)
                for i, username in enumerate(sorted(participants_set))
            ]

            # Create conversation
            conversation = Conversation(
                id=Path(file_path).stem,
                title=f"SMS Conversation",
                messages=messages,
                participants=participants,
                platform='SMS',
                conversation_type='sms',
            )

            conversation.sort_messages()

            self.logger.info(f"Parsed {len(messages)} SMS messages from {len(participants)} participants")

            return conversation

        except ET.ParseError as e:
            raise ValueError(f"Invalid SMS XML: {e}")
        except Exception as e:
            self.logger.error(f"SMS XML parsing failed: {e}")
            raise

    def _parse_mms_message(self, mms_element: ET.Element) -> Optional[Message]:
        """
        Parse MMS message with media attachments from XML.

        Args:
            mms_element: XML element containing MMS data

        Returns:
            Message object with attachments, or None if parsing fails
        """
        try:
            # Extract MMS metadata
            address = mms_element.get('address', 'Unknown')
            contact_name = mms_element.get('contact_name')
            date_ms = mms_element.get('date', '0')
            msg_box = mms_element.get('msg_box', '1')  # 1=received, 2=sent
            subject = mms_element.get('sub', '')  # MMS subject
            readable_date = mms_element.get('readable_date', '')

            # Parse timestamp
            try:
                timestamp_val = int(date_ms)
                if timestamp_val > 10000000000:  # Milliseconds
                    timestamp = datetime.fromtimestamp(timestamp_val / 1000.0)
                else:  # Seconds
                    timestamp = datetime.fromtimestamp(timestamp_val)
            except:
                timestamp = datetime.now()

            # Determine sender
            if msg_box == '2':  # Sent message
                sender = 'Me'
            else:
                if contact_name and contact_name != "(Unknown)":
                    sender = contact_name
                else:
                    sender = address if address else "Unknown"

            # Extract parts (media and text content)
            parts = mms_element.findall('.//part') or mms_element.findall('parts/part')
            attachments = []
            text_parts = []

            for part in parts:
                seq = part.get('seq', '0')
                content_type = part.get('ct', '')
                part_name = part.get('name') or part.get('fn', f'part_{seq}')
                part_text = part.get('text', '')
                part_data = part.get('data', '')  # Base64-encoded data
                content_id = part.get('cl', '')

                # Handle text parts
                if content_type.startswith('text/'):
                    if part_text:
                        text_parts.append(part_text)
                    continue

                # Handle media parts (image, video, audio)
                if part_data:
                    # Determine media type from content-type
                    if content_type.startswith('image/'):
                        media_type = MessageType.IMAGE
                    elif content_type.startswith('video/'):
                        media_type = MessageType.VIDEO
                    elif content_type.startswith('audio/'):
                        media_type = MessageType.AUDIO
                    else:
                        media_type = MessageType.FILE

                    # Create attachment
                    attachment = Attachment(
                        type=media_type,
                        filename=part_name,
                        mime_type=content_type,
                        base64_data=part_data,
                        content_id=content_id,
                        size_bytes=len(part_data) * 3 // 4 if part_data else 0  # Approximate decoded size
                    )
                    attachments.append(attachment)

            # Build message content
            content_parts = []
            if subject:
                content_parts.append(f"Subject: {subject}")
            if text_parts:
                content_parts.extend(text_parts)

            # If no text but has attachments, indicate media presence
            if not content_parts and attachments:
                media_desc = []
                for att in attachments:
                    if att.is_image():
                        media_desc.append(f"📷 {att.filename}")
                    elif att.is_video():
                        media_desc.append(f"🎥 {att.filename}")
                    elif att.is_audio():
                        media_desc.append(f"🎵 {att.filename}")
                    else:
                        media_desc.append(f"📎 {att.filename}")
                content_parts.append("Media: " + ", ".join(media_desc))

            content = "\n".join(content_parts) if content_parts else "(MMS - see attachments)"

            # Create message
            msg = Message(
                id=f"mms_{date_ms}",
                timestamp=timestamp,
                sender=sender,
                content=content,
                type=MessageType.IMAGE if any(a.is_image() for a in attachments) else MessageType.TEXT,
                attachments=attachments,
                platform='MMS',
            )

            return msg

        except Exception as e:
            self.logger.error(f"Failed to parse MMS message: {e}")
            return None

    def _parse_sqlite(self, file_path: str) -> Conversation:
        """Parse iOS SMS SQLite database."""

        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # Query messages from iOS SMS database
            # The schema varies, but typically has a message table
            cursor.execute("""
                SELECT
                    ROWID,
                    text,
                    date,
                    is_from_me,
                    handle_id
                FROM message
                ORDER BY date
            """)

            rows = cursor.fetchall()

            if not rows:
                raise ValueError("No messages found in SMS database")

            # Get handles (phone numbers/contacts)
            cursor.execute("SELECT ROWID, id FROM handle")
            handles = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()

            messages = []
            participants_set = set()

            for row in rows:
                try:
                    msg_id, text, date_val, is_from_me, handle_id = row

                    # Skip empty messages
                    if not text:
                        continue

                    # iOS stores dates as seconds since 2001-01-01
                    # Convert to Unix timestamp
                    ios_epoch = datetime(2001, 1, 1)
                    if date_val:
                        timestamp = ios_epoch + timedelta(seconds=date_val)
                    else:
                        timestamp = datetime.now()

                    # Determine sender
                    if is_from_me:
                        sender = 'Me'
                    else:
                        sender = handles.get(handle_id, 'Unknown')

                    # Create message
                    msg = Message(
                        id=f"sms_{msg_id}",
                        timestamp=timestamp,
                        sender=sender,
                        content=text,
                        type=MessageType.TEXT,
                        platform='SMS',
                    )

                    messages.append(msg)
                    participants_set.add(sender)
                    if sender != 'Me' and handle_id in handles:
                        participants_set.add(handles[handle_id])

                except Exception as e:
                    self.logger.warning(f"Skipping SMS message: {e}")
                    continue

            if not messages:
                raise ValueError("No valid messages found in SMS database")

            # Create participants
            participants = [
                Participant(id=str(i), username=username)
                for i, username in enumerate(sorted(participants_set))
            ]

            # Create conversation
            conversation = Conversation(
                id=Path(file_path).stem,
                title=f"SMS Conversation",
                messages=messages,
                participants=participants,
                platform='SMS',
                conversation_type='sms',
            )

            conversation.sort_messages()

            self.logger.info(f"Parsed {len(messages)} SMS messages from {len(participants)} participants")

            return conversation

        except sqlite3.Error as e:
            raise ValueError(f"Invalid SMS database: {e}")
        except Exception as e:
            self.logger.error(f"SMS database parsing failed: {e}")
            raise
