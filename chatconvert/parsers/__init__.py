"""
Input parsers for various chat formats.

All parsers convert their specific format to the universal Conversation model.
"""

from .base_parser import BaseParser
from .csv_parser import CSVParser
from .json_parser import JSONParser
from .whatsapp_parser import WhatsAppParser
from .generic_text_parser import GenericTextParser
from .excel_parser import ExcelParser
from .sms_parser import SMSParser
from .imessage_parser import iMessageParser
from .messenger_parser import MessengerParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .html_parser import HTMLParser
from .markdown_parser import MarkdownParser

# Parser registry for auto-detection
# Note: JSON parser handles Discord, Slack, Telegram, Messenger auto-detection
PARSERS = {
    'csv': CSVParser,
    'json': JSONParser,  # Auto-detects Discord, Slack, Telegram, Messenger
    'txt': GenericTextParser,  # Universal text parser with WhatsApp + fallback
    'text': GenericTextParser,
    'log': GenericTextParser,  # Log files
    'xlsx': ExcelParser,
    'xls': ExcelParser,
    'xml': SMSParser,  # Android SMS backups
    'db': iMessageParser,  # iMessage/SMS databases (iMessage checked first)
    'sqlite': iMessageParser,
    'pdf': PDFParser,  # PDF chat exports and transcripts
    'docx': DOCXParser,  # Word documents with chat logs
    'doc': DOCXParser,  # Older Word format (python-docx handles both)
    'html': HTMLParser,  # HTML exports, web pages, email threads
    'htm': HTMLParser,
    'md': MarkdownParser,  # Markdown chat logs
    'markdown': MarkdownParser,
}

__all__ = [
    'BaseParser',
    'CSVParser',
    'JSONParser',
    'WhatsAppParser',
    'GenericTextParser',
    'ExcelParser',
    'SMSParser',
    'iMessageParser',
    'MessengerParser',
    'PDFParser',
    'DOCXParser',
    'HTMLParser',
    'MarkdownParser',
    'PARSERS',
]
