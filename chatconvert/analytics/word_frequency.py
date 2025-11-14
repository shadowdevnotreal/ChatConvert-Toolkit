"""
Word Frequency Analyzer - Analyzes word usage patterns.

Provides word frequency statistics, most common words,
and word clouds data.
"""

from typing import Dict, Any, List
from collections import Counter
import re

from .base_analyzer import BaseAnalyzer
from ..models import Conversation


class WordFrequencyAnalyzer(BaseAnalyzer):
    """Analyze word frequency and usage patterns."""

    def __init__(self):
        """Initialize word frequency analyzer."""
        super().__init__()

        # Stopwords to exclude
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how'
        }

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze word frequency in conversation.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dict with word frequency analysis:
            {
                'total_words': int,
                'unique_words': int,
                'most_common': List[Dict],  # [{word, count, frequency}]
                'word_cloud_data': List[Dict],  # Ready for word cloud libraries
                'participant_word_counts': Dict[str, int],
                'average_words_per_message': float,
                'vocabulary_diversity': float  # unique/total ratio
            }
        """
        self._validate_conversation(conversation)

        # Extract all words
        all_words = []
        participant_word_counts = {}
        participants = conversation.get_participants_list()

        for participant in participants:
            participant_word_counts[participant] = 0

        for msg in conversation.messages:
            # Extract words (3+ letters)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', msg.content.lower())
            all_words.extend(words)
            participant_word_counts[msg.sender] += len(words)

        # Total statistics
        total_words = len(all_words)
        unique_words = len(set(all_words))

        # Word frequency
        word_counts = Counter(all_words)

        # Remove stopwords for "most common"
        filtered_counts = {
            word: count for word, count in word_counts.items()
            if word not in self.stopwords
        }

        # Most common words
        most_common = []
        for word, count in Counter(filtered_counts).most_common(50):
            frequency = (count / total_words * 100) if total_words > 0 else 0
            most_common.append({
                'word': word,
                'count': count,
                'frequency': round(frequency, 2)
            })

        # Word cloud data (needs both value and count/size)
        word_cloud_data = [
            {'text': word, 'value': count}
            for word, count in Counter(filtered_counts).most_common(100)
        ]

        # Statistics
        avg_words_per_message = total_words / len(conversation.messages) if conversation.messages else 0
        vocabulary_diversity = unique_words / total_words if total_words > 0 else 0

        return {
            'total_words': total_words,
            'unique_words': unique_words,
            'most_common': most_common,
            'word_cloud_data': word_cloud_data,
            'participant_word_counts': participant_word_counts,
            'average_words_per_message': round(avg_words_per_message, 2),
            'vocabulary_diversity': round(vocabulary_diversity, 3)
        }
