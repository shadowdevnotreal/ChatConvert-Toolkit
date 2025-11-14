"""
Conversion Engine - Orchestrates the complete conversion pipeline.

Auto-detects input formats, selects appropriate parsers and converters,
and manages the conversion process from any input to any output format.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from .models import Conversation, ConversionConfig, ConversionResult
from .parsers import PARSERS, BaseParser
from .converters import CONVERTERS, BaseConverter


class ConversionEngine:
    """
    Main conversion engine that orchestrates the conversion pipeline.

    Features:
    - Auto-detects input format
    - Routes to appropriate parser
    - Routes to appropriate converter
    - Batch conversion support
    - Progress tracking
    - Error handling and logging
    """

    def __init__(self, config: Optional[ConversionConfig] = None):
        """
        Initialize conversion engine.

        Args:
            config: Optional conversion configuration
        """
        self.config = config or ConversionConfig()
        self.logger = logging.getLogger(__name__)

    def convert(
        self,
        input_file: str,
        output_file: str,
        output_format: Optional[str] = None,
        input_format: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> ConversionResult:
        """
        Convert a single file from one format to another.

        Args:
            input_file: Path to input file
            output_file: Path to output file
            output_format: Output format (auto-detected from extension if not provided)
            input_format: Input format (auto-detected if not provided)
            config: Optional converter configuration

        Returns:
            ConversionResult

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If format cannot be detected or is unsupported
        """
        self.logger.info(f"Converting {input_file} → {output_file}")

        # Step 1: Detect input format and select parser
        parser = self._get_parser(input_file, input_format)
        self.logger.info(f"Using parser: {parser.__class__.__name__}")

        # Step 2: Parse input file
        try:
            conversation = parser.parse(input_file)
            self.logger.info(f"Parsed: {len(conversation.messages)} messages, {len(conversation.participants)} participants")
        except Exception as e:
            self.logger.error(f"Parsing failed: {e}")
            return ConversionResult(
                success=False,
                errors=[f"Parsing failed: {e}"]
            )

        # Step 3: Detect output format and select converter
        converter = self._get_converter(output_file, output_format)
        self.logger.info(f"Using converter: {converter.__class__.__name__}")

        # Apply custom config if provided
        if config:
            converter.config.update(config)

        # Step 4: Convert to output format
        try:
            result = converter.convert(conversation, output_file)
            self.logger.info(f"Conversion {'successful' if result.success else 'failed'}")
            return result
        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            return ConversionResult(
                success=False,
                errors=[f"Conversion failed: {e}"]
            )

    def convert_batch(
        self,
        input_files: List[str],
        output_dir: str,
        output_format: str,
        input_format: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ConversionResult]:
        """
        Convert multiple files to the same output format.

        Args:
            input_files: List of input file paths
            output_dir: Output directory
            output_format: Output format for all files
            input_format: Input format (if all files are same format)
            config: Optional converter configuration

        Returns:
            Dict mapping input filenames to ConversionResults
        """
        self.logger.info(f"Batch converting {len(input_files)} files to {output_format}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}

        for input_file in input_files:
            input_path = Path(input_file)
            output_file = output_path / f"{input_path.stem}.{output_format}"

            try:
                result = self.convert(
                    input_file=input_file,
                    output_file=str(output_file),
                    output_format=output_format,
                    input_format=input_format,
                    config=config
                )
                results[input_file] = result
            except Exception as e:
                self.logger.error(f"Failed to convert {input_file}: {e}")
                results[input_file] = ConversionResult(
                    success=False,
                    errors=[str(e)]
                )

        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(f"Batch conversion complete: {successful}/{len(input_files)} successful")

        return results

    def convert_to_multiple_formats(
        self,
        input_file: str,
        output_dir: str,
        output_formats: List[str],
        input_format: Optional[str] = None,
        configs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, ConversionResult]:
        """
        Convert a single input file to multiple output formats.

        Args:
            input_file: Path to input file
            output_dir: Output directory
            output_formats: List of output formats
            input_format: Input format (auto-detected if not provided)
            configs: Optional dict mapping format to converter config

        Returns:
            Dict mapping output format to ConversionResult
        """
        self.logger.info(f"Converting {input_file} to {len(output_formats)} formats")

        # Parse once
        parser = self._get_parser(input_file, input_format)

        try:
            conversation = parser.parse(input_file)
        except Exception as e:
            self.logger.error(f"Parsing failed: {e}")
            error_result = ConversionResult(success=False, errors=[f"Parsing failed: {e}"])
            return {fmt: error_result for fmt in output_formats}

        # Convert to each format
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}
        input_stem = Path(input_file).stem

        for fmt in output_formats:
            output_file = output_path / f"{input_stem}.{fmt}"
            converter = self._get_converter(str(output_file), fmt)

            # Apply format-specific config
            if configs and fmt in configs:
                converter.config.update(configs[fmt])

            try:
                result = converter.convert(conversation, str(output_file))
                results[fmt] = result
            except Exception as e:
                self.logger.error(f"Conversion to {fmt} failed: {e}")
                results[fmt] = ConversionResult(
                    success=False,
                    errors=[f"Conversion failed: {e}"]
                )

        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(f"Multi-format conversion complete: {successful}/{len(output_formats)} successful")

        return results

    def _get_parser(self, file_path: str, format_hint: Optional[str] = None) -> BaseParser:
        """
        Get appropriate parser for input file.

        Args:
            file_path: Path to input file
            format_hint: Optional format hint

        Returns:
            Parser instance

        Raises:
            ValueError: If no suitable parser found
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        # If format hint provided, use it
        if format_hint:
            format_hint = format_hint.lower().lstrip('.')
            if format_hint in PARSERS:
                parser_class = PARSERS[format_hint]
                parser = parser_class()
                if parser.can_parse(file_path):
                    return parser

        # Auto-detect based on extension
        ext = path.suffix.lstrip('.').lower()
        if ext in PARSERS:
            parser_class = PARSERS[ext]
            parser = parser_class()
            if parser.can_parse(file_path):
                return parser

        # Try all parsers (brute force)
        for parser_class in set(PARSERS.values()):
            try:
                parser = parser_class()
                if parser.can_parse(file_path):
                    return parser
            except Exception:
                continue

        raise ValueError(f"No suitable parser found for: {file_path}")

    def _get_converter(self, output_file: str, format_hint: Optional[str] = None) -> BaseConverter:
        """
        Get appropriate converter for output format.

        Args:
            output_file: Path to output file
            format_hint: Optional format hint

        Returns:
            Converter instance

        Raises:
            ValueError: If format is unsupported
        """
        # If format hint provided, use it
        if format_hint:
            format_hint = format_hint.lower().lstrip('.')
            if format_hint in CONVERTERS:
                return CONVERTERS[format_hint]()

        # Auto-detect based on extension
        ext = Path(output_file).suffix.lstrip('.').lower()
        if ext in CONVERTERS:
            return CONVERTERS[ext]()

        raise ValueError(f"Unsupported output format: {ext}")

    def list_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get list of all supported input and output formats.

        Returns:
            Dict with 'input' and 'output' keys listing supported formats
        """
        return {
            'input': sorted(set(PARSERS.keys())),
            'output': sorted(set(CONVERTERS.keys()))
        }

    def get_parser_info(self, format: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific parser.

        Args:
            format: Format name

        Returns:
            Dict with parser information or None if not found
        """
        format = format.lower()
        if format not in PARSERS:
            return None

        parser_class = PARSERS[format]
        return {
            'name': parser_class.__name__,
            'format': format,
            'description': parser_class.__doc__ or '',
        }

    def get_converter_info(self, format: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific converter.

        Args:
            format: Format name

        Returns:
            Dict with converter information or None if not found
        """
        format = format.lower()
        if format not in CONVERTERS:
            return None

        converter_class = CONVERTERS[format]
        return {
            'name': converter_class.__name__,
            'format': format,
            'description': converter_class.__doc__ or '',
        }
