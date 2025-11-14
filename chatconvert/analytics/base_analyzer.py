"""
Base analyzer class for all analytics modules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

from ..models import Conversation


class BaseAnalyzer(ABC):
    """Base class for all conversation analyzers."""

    def __init__(self):
        """Initialize analyzer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze a conversation.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dictionary containing analysis results
        """
        pass

    def _validate_conversation(self, conversation: Conversation):
        """
        Validate conversation has data.

        Args:
            conversation: Conversation to validate

        Raises:
            ValueError: If conversation is invalid
        """
        if not conversation.messages:
            raise ValueError("Conversation has no messages")
