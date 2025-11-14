"""
ChatConvert Toolkit - Universal Chat Conversion & Analytics Platform

A comprehensive toolkit for converting chat logs from various platforms
into multiple formats with powerful analytics and visualization.

Version: 2.0.0
Python: 3.6+
License: MIT
"""

__version__ = "2.0.0"
__author__ = "ChatConvert Toolkit Team"
__license__ = "MIT"

from .engine import ConversionEngine
from .models import Message, Conversation, ConversionConfig

__all__ = [
    "ConversionEngine",
    "Message",
    "Conversation",
    "ConversionConfig",
]
