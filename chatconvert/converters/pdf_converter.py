"""
PDF Converter - Create professional PDF documents from conversations.

Features:
- Color-coded participants
- Page headers and footers
- Statistics tables
- Automatic page breaks
- Professional formatting
- Table of contents (optional)
"""

import time
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from .base_converter import BaseConverter
from ..models import Conversation, ConversionResult


class PDFConverter(BaseConverter):
    """Convert conversations to PDF format."""

    def get_file_extension(self) -> str:
        return 'pdf'

    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert conversation to PDF.

        Config options:
        - page_size: 'letter' or 'a4' (default: 'letter')
        - include_stats: Include statistics table (default: True)
        - color_coded: Color-code participants (default: True)

        Args:
            conversation: Conversation to convert
            output_file: Path to output .pdf file

        Returns:
            ConversionResult

        Raises:
            ImportError: If reportlab is not installed
        """
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF conversion. Install with: pip install reportlab")

        start_time = time.time()
        path = self._validate_output_path(output_file)

        try:
            # Get config
            page_size_name = self.config.get('page_size', 'letter')
            include_stats = self.config.get('include_stats', True)
            color_coded = self.config.get('color_coded', True)

            # Set page size
            page_size = letter if page_size_name == 'letter' else A4

            # Generate PDF
            self._generate_pdf(
                conversation,
                str(path),
                page_size=page_size,
                include_stats=include_stats,
                color_coded=color_coded
            )

            processing_time = time.time() - start_time

            return self._create_result(
                success=True,
                output_file=str(path),
                message_count=len(conversation.messages),
                processing_time=processing_time,
                statistics={
                    'page_size': page_size_name,
                    'participants': len(conversation.get_participants_list()),
                }
            )

        except Exception as e:
            self.logger.error(f"PDF conversion failed: {e}")
            return self._create_result(
                success=False,
                errors=[str(e)],
                processing_time=time.time() - start_time
            )

    def _generate_pdf(
        self,
        conversation: Conversation,
        output_path: str,
        page_size=None,
        include_stats: bool = True,
        color_coded: bool = True
    ):
        """Generate PDF document."""

        # Default to letter if not specified
        if page_size is None:
            page_size = letter

        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )

        # Container for document elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=TA_CENTER
        )

        # Color palette for participants
        participant_colors = [
            colors.HexColor('#667eea'),
            colors.HexColor('#764ba2'),
            colors.HexColor('#f093fb'),
            colors.HexColor('#4facfe'),
            colors.HexColor('#43e97b'),
        ]

        # Map participants to colors
        participants = conversation.get_participants_list()
        participant_color_map = {}
        for i, p in enumerate(participants):
            participant_color_map[p] = participant_colors[i % len(participant_colors)]

        # Title
        elements.append(Paragraph(f"💬 {conversation.title}", title_style))

        # Subtitle
        date_range = conversation.get_date_range()
        if date_range[0]:
            start = date_range[0].strftime('%Y-%m-%d')
            end = date_range[1].strftime('%Y-%m-%d')
            if start == end:
                date_str = f"Date: {start}"
            else:
                date_str = f"Period: {start} to {end}"
        else:
            date_str = ""

        elements.append(Paragraph(
            f"{conversation.platform} Conversation<br/>{date_str}",
            subtitle_style
        ))

        elements.append(Spacer(1, 0.3*inch))

        # Statistics table
        if include_stats:
            elements.extend(self._create_statistics_table(conversation, participant_color_map))
            elements.append(PageBreak())

        # Messages
        message_style = ParagraphStyle(
            'Message',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=6
        )

        for msg in conversation.messages:
            # Sender and timestamp
            sender_color = participant_color_map.get(msg.sender, colors.black) if color_coded else colors.HexColor('#667eea')

            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')

            sender_style = ParagraphStyle(
                'Sender',
                parent=styles['Normal'],
                fontSize=11,
                textColor=sender_color,
                fontName='Helvetica-Bold',
                spaceAfter=4
            )

            # Sender header
            elements.append(Paragraph(f"{msg.sender} - {timestamp}", sender_style))

            # Message content
            content = msg.content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(content, message_style))
            elements.append(Spacer(1, 0.15*inch))

        # Build PDF
        doc.build(elements)

    def _create_statistics_table(self, conversation: Conversation, color_map: dict) -> list:
        """Create statistics table."""

        elements = []
        styles = getSampleStyleSheet()

        # Section title
        stats_title = ParagraphStyle(
            'StatsTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12
        )

        elements.append(Paragraph("📊 Conversation Statistics", stats_title))
        elements.append(Spacer(1, 0.1*inch))

        # Calculate stats
        participants = conversation.get_participants_list()
        participant_stats = []

        for p in participants:
            count = sum(1 for m in conversation.messages if m.sender == p)
            percentage = (count / len(conversation.messages) * 100) if conversation.messages else 0
            participant_stats.append([p, str(count), f"{percentage:.1f}%"])

        # Sort by message count
        participant_stats.sort(key=lambda x: int(x[1]), reverse=True)

        # Table data
        table_data = [
            ['Participant', 'Messages', 'Percentage']
        ] + participant_stats

        # Create table
        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])

        # Table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

        # Color-code rows
        for i, (username, _, _) in enumerate(participant_stats, 1):
            if username in color_map:
                table_style.add('TEXTCOLOR', (0, i), (0, i), color_map[username])

        table.setStyle(table_style)
        elements.append(table)

        # Overall stats
        elements.append(Spacer(1, 0.2*inch))

        overall_style = ParagraphStyle(
            'Overall',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4
        )

        elements.append(Paragraph(f"<b>Total Messages:</b> {len(conversation.messages)}", overall_style))
        elements.append(Paragraph(f"<b>Total Participants:</b> {len(participants)}", overall_style))

        return elements
