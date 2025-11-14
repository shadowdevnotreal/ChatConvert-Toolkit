"""
Base parser class that all input parsers inherit from.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from ..models import Conversation


logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """
    Abstract base class for all input parsers.

    All parsers must implement:
    - can_parse(): Check if parser can handle the file
    - parse(): Convert file to Conversation object
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize parser.

        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if parser can handle the file
        """
        pass

    @abstractmethod
    def parse(self, file_path: str) -> Conversation:
        """
        Parse the file and return a Conversation object.

        Args:
            file_path: Path to the file to parse

        Returns:
            Conversation object containing all messages

        Raises:
            ValueError: If file cannot be parsed
            FileNotFoundError: If file doesn't exist
        """
        pass

    def _read_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Helper to read file content.

        Args:
            file_path: Path to file
            encoding: File encoding

        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        self.logger.warning(f"Using {enc} encoding for {file_path}")
                        return f.read()
                except:
                    continue
            raise ValueError(f"Could not decode file {file_path}")

    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension in lowercase."""
        return Path(file_path).suffix.lower().lstrip('.')

    def _validate_file(self, file_path: str) -> None:
        """
        Validate that file exists and is readable.

        Args:
            file_path: Path to file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not readable
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        if not path.stat().st_size > 0:
            raise ValueError(f"File is empty: {file_path}")

    def get_name(self) -> str:
        """Get parser name."""
        return self.__class__.__name__.replace('Parser', '')

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
