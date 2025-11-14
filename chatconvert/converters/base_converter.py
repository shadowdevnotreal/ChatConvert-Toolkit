"""
Base converter class that all output converters inherit from.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from ..models import Conversation, ConversionResult
import time


logger = logging.getLogger(__name__)


class BaseConverter(ABC):
    """
    Abstract base class for all output converters.

    All converters must implement:
    - get_file_extension(): Return the output file extension
    - convert(): Convert Conversation to output format
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize converter.

        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get the file extension for this output format.

        Returns:
            File extension (e.g., 'html', 'pdf', 'json')
        """
        pass

    @abstractmethod
    def convert(self, conversation: Conversation, output_file: str) -> ConversionResult:
        """
        Convert a Conversation object to the output format.

        Args:
            conversation: Conversation object to convert
            output_file: Path to the output file

        Returns:
            ConversionResult with success status and metadata

        Raises:
            ValueError: If conversion fails
        """
        pass

    def _create_result(
        self,
        success: bool,
        output_file: Optional[str] = None,
        message_count: int = 0,
        processing_time: float = 0.0,
        warnings: Optional[list] = None,
        errors: Optional[list] = None,
        statistics: Optional[dict] = None
    ) -> ConversionResult:
        """
        Helper to create a ConversionResult.

        Args:
            success: Whether conversion succeeded
            output_file: Path to output file
            message_count: Number of messages converted
            processing_time: Time taken in seconds
            warnings: List of warning messages
            errors: List of error messages
            statistics: Statistics dict

        Returns:
            ConversionResult object
        """
        return ConversionResult(
            success=success,
            output_file=output_file,
            format=self.get_file_extension(),
            message_count=message_count,
            processing_time=processing_time,
            warnings=warnings or [],
            errors=errors or [],
            statistics=statistics or {}
        )

    def _validate_output_path(self, output_file: str) -> Path:
        """
        Validate and prepare output path.

        Args:
            output_file: Path to output file

        Returns:
            Path object

        Raises:
            ValueError: If path is invalid
        """
        path = Path(output_file)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Add extension if missing
        if not path.suffix:
            path = path.with_suffix(f'.{self.get_file_extension()}')

        return path

    def _write_file(self, path: Path, content: str, encoding: str = 'utf-8'):
        """
        Write content to file safely.

        Args:
            path: Path to file
            content: Content to write
            encoding: File encoding
        """
        try:
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Failed to write file {path}: {e}")
            raise

    def _write_binary(self, path: Path, content: bytes):
        """
        Write binary content to file safely.

        Args:
            path: Path to file
            content: Binary content to write
        """
        try:
            with open(path, 'wb') as f:
                f.write(content)
        except Exception as e:
            self.logger.error(f"Failed to write file {path}: {e}")
            raise

    def get_name(self) -> str:
        """Get converter name."""
        return self.__class__.__name__.replace('Converter', '')

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class TemplateConverter(BaseConverter):
    """
    Base class for template-based converters.

    Provides template rendering utilities for converters that use templates.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.template_dir = Path(__file__).parent.parent / 'templates'

    def _load_template(self, template_name: str) -> str:
        """
        Load a template file.

        Args:
            template_name: Name of template file

        Returns:
            Template content as string
        """
        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Simple template rendering (can be upgraded to Jinja2 later).

        Args:
            template: Template string
            context: Variables to substitute

        Returns:
            Rendered template
        """
        result = template

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))

        return result
