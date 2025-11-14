"""
XSL Transformer - Apply XSLT stylesheets to XML files.

Provides utilities for:
- Transforming XML using XSL stylesheets
- Styling XML previews with custom XSL
- Pre-processing XML before parsing
- Exporting XML with custom styling
"""

import logging
from pathlib import Path
from typing import Optional, Union

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    etree = None


class XSLTransformer:
    """
    Apply XSL transformations to XML documents.

    Requires lxml library for XSLT processing.
    """

    def __init__(self):
        """Initialize XSL transformer."""
        self.logger = logging.getLogger(__name__)

        if not HAS_LXML:
            self.logger.warning("lxml not installed. XSL transformations unavailable.")

    def is_available(self) -> bool:
        """Check if XSL transformation is available."""
        return HAS_LXML

    def transform(
        self,
        xml_path: Union[str, Path],
        xsl_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Transform XML using XSL stylesheet.

        Args:
            xml_path: Path to XML file
            xsl_path: Path to XSL/XSLT stylesheet
            output_path: Optional path to save transformed output

        Returns:
            Transformed output as string (usually HTML)

        Raises:
            ImportError: If lxml is not installed
            ValueError: If XML or XSL is invalid
            FileNotFoundError: If files don't exist
        """
        if not HAS_LXML:
            raise ImportError("lxml library required for XSL transformations. Install with: pip install lxml>=4.9.0")

        xml_path = Path(xml_path)
        xsl_path = Path(xsl_path)

        if not xml_path.exists():
            raise FileNotFoundError(f"XML file not found: {xml_path}")
        if not xsl_path.exists():
            raise FileNotFoundError(f"XSL file not found: {xsl_path}")

        try:
            # Parse XML
            xml_doc = etree.parse(str(xml_path))

            # Parse XSL stylesheet
            xsl_doc = etree.parse(str(xsl_path))
            transform = etree.XSLT(xsl_doc)

            # Apply transformation
            result = transform(xml_doc)

            # Convert to string
            output = str(result)

            # Save to file if output path provided
            if output_path:
                output_path = Path(output_path)
                output_path.write_text(output, encoding='utf-8')
                self.logger.info(f"Transformed XML saved to: {output_path}")

            return output

        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML syntax error: {e}")
        except etree.XSLTParseError as e:
            raise ValueError(f"XSL stylesheet error: {e}")
        except etree.XSLTApplyError as e:
            raise ValueError(f"XSL transformation error: {e}")
        except Exception as e:
            self.logger.error(f"XSL transformation failed: {e}")
            raise

    def transform_string(
        self,
        xml_string: str,
        xsl_string: str
    ) -> str:
        """
        Transform XML string using XSL stylesheet string.

        Args:
            xml_string: XML content as string
            xsl_string: XSL stylesheet as string

        Returns:
            Transformed output as string

        Raises:
            ImportError: If lxml is not installed
            ValueError: If XML or XSL is invalid
        """
        if not HAS_LXML:
            raise ImportError("lxml library required for XSL transformations")

        try:
            # Parse XML from string
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))

            # Parse XSL from string
            xsl_doc = etree.fromstring(xsl_string.encode('utf-8'))
            transform = etree.XSLT(xsl_doc)

            # Apply transformation
            result = transform(xml_doc)

            return str(result)

        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML syntax error: {e}")
        except etree.XSLTParseError as e:
            raise ValueError(f"XSL stylesheet error: {e}")
        except etree.XSLTApplyError as e:
            raise ValueError(f"XSL transformation error: {e}")
        except Exception as e:
            self.logger.error(f"XSL transformation failed: {e}")
            raise

    def validate_xsl(self, xsl_path: Union[str, Path]) -> bool:
        """
        Validate XSL stylesheet.

        Args:
            xsl_path: Path to XSL file

        Returns:
            True if valid, False otherwise
        """
        if not HAS_LXML:
            return False

        try:
            xsl_path = Path(xsl_path)
            if not xsl_path.exists():
                return False

            xsl_doc = etree.parse(str(xsl_path))
            etree.XSLT(xsl_doc)
            return True

        except:
            return False

    def get_default_preview_xsl(self) -> str:
        """
        Get default XSL stylesheet for XML preview.

        Returns:
            XSL stylesheet as string for basic XML to HTML conversion
        """
        return """<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>

    <xsl:template match="/">
        <html>
            <head>
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
                    .xml-element { margin-left: 20px; }
                    .xml-tag { color: #0066cc; font-weight: bold; }
                    .xml-attribute { color: #cc6600; }
                    .xml-value { color: #006600; }
                    .xml-text { color: #333; }
                    table { border-collapse: collapse; width: 100%; margin: 10px 0; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <h2>XML Preview</h2>
                <xsl:apply-templates/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="*">
        <div class="xml-element">
            <span class="xml-tag">&lt;<xsl:value-of select="name()"/></span>
            <xsl:for-each select="@*">
                <span class="xml-attribute"> <xsl:value-of select="name()"/>="<xsl:value-of select="."/>"</span>
            </xsl:for-each>
            <span class="xml-tag">&gt;</span>

            <xsl:choose>
                <xsl:when test="*">
                    <xsl:apply-templates/>
                </xsl:when>
                <xsl:otherwise>
                    <span class="xml-text"><xsl:value-of select="."/></span>
                </xsl:otherwise>
            </xsl:choose>

            <span class="xml-tag">&lt;/<xsl:value-of select="name()"/>&gt;</span>
        </div>
    </xsl:template>
</xsl:stylesheet>"""


def create_default_xsl_file(output_path: Union[str, Path]) -> None:
    """
    Create default XSL stylesheet file for XML preview.

    Args:
        output_path: Path where to save the XSL file
    """
    transformer = XSLTransformer()
    default_xsl = transformer.get_default_preview_xsl()

    output_path = Path(output_path)
    output_path.write_text(default_xsl, encoding='utf-8')
