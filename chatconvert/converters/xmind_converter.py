"""
XMind 8 Mindmap Converter.

Converts conversations to XMind 8 format (.xmind files).
XMind 8 files are ZIP archives containing XML files.

Format Structure:
- content.xml: Mind map structure
- meta.xml: Metadata
- styles.xml: Visual styling
- manifest.xml: File listing

Compatible with XMind 8 (Java version), not XMind 2022+
"""

import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import uuid

from .base_converter import BaseConverter
from ..models import Conversation, ConversionResult, Message


class XMindConverter(BaseConverter):
    """Convert conversations to XMind 8 mindmap format."""

    def get_file_extension(self) -> str:
        return 'xmind'

    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert conversation to XMind 8 format.

        Creates a mind map with:
        - Central topic: Conversation title
        - Main branches: Time periods or participants
        - Sub-branches: Individual messages

        Args:
            conversation: Conversation to convert
            output_file: Path to output .xmind file

        Returns:
            ConversionResult
        """
        start_time = time.time()
        path = self._validate_output_path(output_file)

        try:
            # Generate XML files
            content_xml = self._generate_content_xml(conversation)
            meta_xml = self._generate_meta_xml(conversation)
            styles_xml = self._generate_styles_xml()
            manifest_xml = self._generate_manifest_xml()

            # Create ZIP archive
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('content.xml', content_xml)
                zf.writestr('meta.xml', meta_xml)
                zf.writestr('styles.xml', styles_xml)
                zf.writestr('META-INF/manifest.xml', manifest_xml)

            processing_time = time.time() - start_time

            return self._create_result(
                success=True,
                output_file=str(path),
                message_count=len(conversation.messages),
                processing_time=processing_time,
                statistics={
                    'participants': len(conversation.get_participants_list()),
                    'format': 'XMind 8',
                }
            )

        except Exception as e:
            self.logger.error(f"XMind conversion failed: {e}")
            return self._create_result(
                success=False,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _generate_content_xml(self, conversation: Conversation) -> str:
        """Generate the main content.xml file."""
        # Create root elements
        xmap_content = ET.Element('xmap-content', {
            'xmlns': 'urn:xmind:xmap:xmlns:content:2.0',
            'xmlns:fo': 'http://www.w3.org/1999/XSL/Format',
            'xmlns:svg': 'http://www.w3.org/2000/svg',
            'xmlns:xhtml': 'http://www.w3.org/1999/xhtml',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'version': '2.0'
        })

        sheet = ET.SubElement(xmap_content, 'sheet', {
            'id': self._generate_id(),
            'theme': 'classic'
        })

        # Central topic
        root_topic = ET.SubElement(sheet, 'topic', {
            'id': self._generate_id(),
            'structure-class': 'org.xmind.ui.map.unbalanced'
        })

        title = ET.SubElement(root_topic, 'title')
        title.text = conversation.title

        # Add participants branch
        participants = conversation.get_participants_list()
        if participants:
            participants_topic = self._add_topic(root_topic, f"Participants ({len(participants)})")
            for participant in participants:
                msg_count = sum(1 for m in conversation.messages if m.sender == participant)
                self._add_topic(participants_topic, f"{participant} ({msg_count} messages)")

        # Add statistics branch
        stats_topic = self._add_topic(root_topic, "Statistics")
        self._add_topic(stats_topic, f"Total Messages: {len(conversation.messages)}")

        date_range = conversation.get_date_range()
        if date_range[0]:
            start_date = date_range[0].strftime('%Y-%m-%d')
            end_date = date_range[1].strftime('%Y-%m-%d')
            self._add_topic(stats_topic, f"Period: {start_date} to {end_date}")

        # Add conversation by time periods
        self._add_messages_by_time(root_topic, conversation)

        # Add conversation by participant
        self._add_messages_by_participant(root_topic, conversation)

        # Convert to string
        return self._prettify_xml(xmap_content)

    def _add_messages_by_time(self, parent: ET.Element, conversation: Conversation):
        """Add messages organized by time period."""
        time_topic = self._add_topic(parent, "Timeline")

        # Group by date
        by_date = {}
        for msg in conversation.messages:
            date_key = msg.timestamp.strftime('%Y-%m-%d')
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(msg)

        # Add each date
        for date_key in sorted(by_date.keys()):
            messages = by_date[date_key]
            date_topic = self._add_topic(time_topic, f"{date_key} ({len(messages)} messages)")

            # Add first few messages as examples
            for msg in messages[:5]:  # Limit to prevent huge maps
                time_str = msg.timestamp.strftime('%H:%M')
                content = msg.content[:50] + '...' if len(msg.content) > 50 else msg.content
                self._add_topic(date_topic, f"[{time_str}] {msg.sender}: {content}")

            if len(messages) > 5:
                self._add_topic(date_topic, f"... and {len(messages) - 5} more messages")

    def _add_messages_by_participant(self, parent: ET.Element, conversation: Conversation):
        """Add messages organized by participant."""
        participants_topic = self._add_topic(parent, "By Participant")

        # Group by sender
        by_sender = {}
        for msg in conversation.messages:
            if msg.sender not in by_sender:
                by_sender[msg.sender] = []
            by_sender[msg.sender].append(msg)

        # Add each participant
        for sender in sorted(by_sender.keys()):
            messages = by_sender[sender]
            sender_topic = self._add_topic(participants_topic, f"{sender} ({len(messages)})")

            # Add sample messages
            for msg in messages[:3]:  # Limit to prevent huge maps
                content = msg.content[:50] + '...' if len(msg.content) > 50 else msg.content
                time_str = msg.timestamp.strftime('%Y-%m-%d %H:%M')
                self._add_topic(sender_topic, f"[{time_str}] {content}")

            if len(messages) > 3:
                self._add_topic(sender_topic, f"... and {len(messages) - 3} more messages")

    def _add_topic(self, parent: ET.Element, title: str) -> ET.Element:
        """Add a topic to the mind map."""
        # Find or create children element
        children = parent.find('children')
        if children is None:
            children = ET.SubElement(parent, 'children')

        # Find or create topics element
        topics = children.find('topics')
        if topics is None:
            topics = ET.SubElement(children, 'topics', {'type': 'attached'})

        # Create topic
        topic = ET.SubElement(topics, 'topic', {'id': self._generate_id()})
        title_elem = ET.SubElement(topic, 'title')
        title_elem.text = title

        return topic

    def _generate_meta_xml(self, conversation: Conversation) -> str:
        """Generate meta.xml file."""
        meta = ET.Element('meta', {
            'xmlns': 'urn:xmind:xmap:xmlns:meta:2.0',
            'version': '2.0'
        })

        # Add metadata
        ET.SubElement(meta, 'Author').text = 'ChatConvert Toolkit'
        ET.SubElement(meta, 'Create').text = datetime.now().isoformat()

        return self._prettify_xml(meta)

    def _generate_styles_xml(self) -> str:
        """Generate styles.xml file."""
        styles = ET.Element('xmap-styles', {
            'xmlns': 'urn:xmind:xmap:xmlns:style:2.0',
            'version': '2.0'
        })

        # Add default style
        style = ET.SubElement(styles, 'style', {
            'id': self._generate_id(),
            'type': 'topic'
        })

        return self._prettify_xml(styles)

    def _generate_manifest_xml(self) -> str:
        """Generate META-INF/manifest.xml file."""
        manifest = ET.Element('manifest', {
            'xmlns': 'urn:xmind:xmap:xmlns:manifest:1.0'
        })

        # Add file entries
        ET.SubElement(manifest, 'file-entry', {
            'full-path': 'content.xml',
            'media-type': 'text/xml'
        })

        ET.SubElement(manifest, 'file-entry', {
            'full-path': 'META-INF/',
            'media-type': ''
        })

        ET.SubElement(manifest, 'file-entry', {
            'full-path': 'meta.xml',
            'media-type': 'text/xml'
        })

        ET.SubElement(manifest, 'file-entry', {
            'full-path': 'styles.xml',
            'media-type': 'text/xml'
        })

        return self._prettify_xml(manifest)

    def _generate_id(self) -> str:
        """Generate a unique ID for XMind elements."""
        return str(uuid.uuid4()).replace('-', '')[:16]

    def _prettify_xml(self, elem: ET.Element) -> str:
        """Convert XML element to pretty-printed string."""
        from xml.dom import minidom

        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ', encoding='UTF-8').decode('utf-8')


import time
