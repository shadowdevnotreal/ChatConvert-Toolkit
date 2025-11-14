"""
Web interface module for ChatConvert-Toolkit.

Provides Flask-based REST API and web UI for conversions and analytics.
"""

from .app import create_app

__all__ = ['create_app']
