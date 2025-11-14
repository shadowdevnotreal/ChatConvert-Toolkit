#!/usr/bin/env python3
"""
CSV to PDF Converter for Chat Logs
Converts chat conversation CSV files into formatted PDF documents.
"""

import csv
import os
from datetime import datetime

# Check if reportlab is available
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def csv_to_pdf(csv_file_path='chat.csv', output_file='chat_conversation.pdf'):
    """
    Convert a CSV chat log to a PDF file.

    Args:
        csv_file_path: Path to the input CSV file
        output_file: Path to the output PDF file

    Expected CSV format:
        timestamp, username, message
    """

    if not REPORTLAB_AVAILABLE:
        print("Error: reportlab library not installed!")
        print("Please install it using: pip install reportlab")
        return False

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found!")
        return False

    try:
        # Read CSV data
        messages = []
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                messages.append(row)

        if not messages:
            print("Warning: No messages found in CSV file!")
            return False

        # Generate PDF
        create_pdf(messages, output_file)

        print(f"✓ Successfully converted {len(messages)} messages to PDF!")
        print(f"✓ Output file: {output_file}")
        return True

    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_pdf(messages, output_file):
    """Create PDF document from messages."""

    # Create PDF document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for PDF elements
    story = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    username_style = ParagraphStyle(
        'Username',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#667eea'),
        fontName='Helvetica-Bold',
    )

    timestamp_style = ParagraphStyle(
        'Timestamp',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
    )

    message_style = ParagraphStyle(
        'Message',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15,
        leftIndent=20,
    )

    # Add title
    story.append(Paragraph("💬 Chat Conversation", title_style))
    story.append(Paragraph(f"Converted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 0.3 * inch))

    # Add messages
    for i, msg in enumerate(messages):
        username = msg.get('username', 'Unknown')
        timestamp = msg.get('timestamp', '')
        message = msg.get('message', '')

        # Escape special characters for XML
        username = escape_xml(username)
        message = escape_xml(message)
        timestamp = escape_xml(timestamp)

        # Create message block
        story.append(Paragraph(f"<b>{username}</b> <font color='grey' size='8'>{timestamp}</font>", username_style))
        story.append(Paragraph(message, message_style))

        # Add line separator every few messages
        if (i + 1) % 5 == 0:
            story.append(Spacer(1, 0.1 * inch))

        # Add page break if too many messages
        if (i + 1) % 30 == 0 and i < len(messages) - 1:
            story.append(PageBreak())

    # Add footer with statistics
    story.append(Spacer(1, 0.5 * inch))
    stats_data = [
        ['Total Messages', str(len(messages))],
        ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ]

    stats_table = Table(stats_data, colWidths=[2*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    story.append(stats_table)

    # Build PDF
    doc.build(story)


def escape_xml(text):
    """Escape special XML characters."""
    if not isinstance(text, str):
        return str(text)

    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')

    return text


if __name__ == "__main__":
    print("=" * 50)
    print("CSV to PDF Converter")
    print("=" * 50)

    if not REPORTLAB_AVAILABLE:
        print("\n⚠️  reportlab library is required for PDF conversion")
        print("Install it using: pip install reportlab\n")
        exit(1)

    # Look for CSV files in current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

    if csv_files:
        print(f"\nFound CSV files: {', '.join(csv_files)}")
        csv_file = csv_files[0] if 'chat.csv' not in csv_files else 'chat.csv'
    else:
        csv_file = 'chat.csv'

    print(f"Using: {csv_file}\n")

    csv_to_pdf(csv_file)
