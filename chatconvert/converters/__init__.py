"""
Output converters for various formats.

All converters take a Conversation object and generate output files.
"""

from .base_converter import BaseConverter
from .html_converter import HTMLConverter
from .markdown_converter import MarkdownConverter
from .pdf_converter import PDFConverter
from .sqlite_converter import SQLiteConverter
from .json_converter import JSONConverter
from .txt_converter import TXTConverter
from .xmind_converter import XMindConverter
from .docx_converter import DOCXConverter

# Converter registry
CONVERTERS = {
    'html': HTMLConverter,
    'md': MarkdownConverter,
    'markdown': MarkdownConverter,
    'pdf': PDFConverter,
    'db': SQLiteConverter,
    'sqlite': SQLiteConverter,
    'json': JSONConverter,
    'txt': TXTConverter,
    'text': TXTConverter,
    'xmind': XMindConverter,
    'docx': DOCXConverter,
    'doc': DOCXConverter,
}

__all__ = [
    'BaseConverter',
    'HTMLConverter',
    'MarkdownConverter',
    'PDFConverter',
    'SQLiteConverter',
    'JSONConverter',
    'TXTConverter',
    'XMindConverter',
    'DOCXConverter',
    'CONVERTERS',
]
