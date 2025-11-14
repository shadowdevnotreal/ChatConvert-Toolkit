"""
Topic Analyzer - Identifies main topics and themes in conversations.

Uses keyword extraction and AI-powered topic modeling to identify
what the conversation is about.
"""

import os
from typing import Dict, Any, List, Optional, Set
from collections import Counter
import re

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from .base_analyzer import BaseAnalyzer
from .groq_model_manager import GroqModelManager, AnalysisTask
from ..models import Conversation


class TopicAnalyzer(BaseAnalyzer):
    """Analyze topics and themes in conversations."""

    def __init__(self, api_key: Optional[str] = None, use_ai: bool = True):
        """
        Initialize topic analyzer.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            use_ai: Whether to use AI analysis
        """
        super().__init__()
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.use_ai = use_ai and HAS_GROQ and self.api_key
        self.model_manager = GroqModelManager()

        if self.use_ai:
            self.client = Groq(api_key=self.api_key)
            # Use model manager for topic extraction
            self.model = self.model_manager.select_model(AnalysisTask.TOPIC_EXTRACTION)

        # Common stopwords to filter out
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'my',
            'me', 'your', 'his', 'her', 'its', 'our', 'their', 'im', 'ive', 'dont'
        }

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze topics in conversation.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dict with topic analysis:
            {
                'main_topics': List[str],
                'keywords': List[Dict],  # [{word, count, relevance}]
                'topic_distribution': Dict[str, int],
                'participant_topics': Dict[str, List[str]],
                'method': str
            }
        """
        self._validate_conversation(conversation)

        if self.use_ai:
            return self._analyze_with_ai(conversation)
        else:
            return self._analyze_with_keywords(conversation)

    def _analyze_with_ai(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze topics using Groq AI."""
        self.logger.info("Analyzing topics with Groq AI")

        # Sample messages for AI analysis (to reduce token usage)
        sample_size = min(100, len(conversation.messages))
        step = len(conversation.messages) // sample_size
        sampled_messages = conversation.messages[::max(1, step)][:sample_size]

        # Create conversation summary
        messages_text = "\n".join([
            f"[{msg.sender}]: {msg.content}"
            for msg in sampled_messages
        ])

        prompt = f"""Analyze this conversation and identify the main topics being discussed.

Conversation:
{messages_text[:4000]}

List the top 5-7 main topics discussed. Format: one topic per line, concise.
Topics:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )

            topics_text = response.choices[0].message.content.strip()
            main_topics = [
                topic.strip().lstrip('1234567890.-) ')
                for topic in topics_text.split('\n')
                if topic.strip()
            ][:7]

        except Exception as e:
            self.logger.warning(f"AI topic extraction failed: {e}")
            main_topics = []

        # Combine AI topics with keyword analysis
        keyword_results = self._extract_keywords(conversation)

        # Get per-participant keywords
        participant_topics = self._analyze_participant_topics(conversation)

        return {
            'main_topics': main_topics,
            'keywords': keyword_results['keywords'][:20],
            'topic_distribution': keyword_results['topic_distribution'],
            'participant_topics': participant_topics,
            'method': 'ai',
            'total_messages_analyzed': len(sampled_messages)
        }

    def _analyze_with_keywords(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze topics using keyword extraction."""
        self.logger.info("Analyzing topics with keyword extraction")

        keyword_results = self._extract_keywords(conversation)
        participant_topics = self._analyze_participant_topics(conversation)

        # Generate main topics from top keywords
        main_topics = [kw['word'] for kw in keyword_results['keywords'][:7]]

        return {
            'main_topics': main_topics,
            'keywords': keyword_results['keywords'][:20],
            'topic_distribution': keyword_results['topic_distribution'],
            'participant_topics': participant_topics,
            'method': 'keyword',
            'total_messages_analyzed': len(conversation.messages)
        }

    def _extract_keywords(self, conversation: Conversation) -> Dict[str, Any]:
        """Extract keywords from conversation."""

        # Collect all words
        all_text = ' '.join([msg.content for msg in conversation.messages])
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())

        # Filter stopwords and count
        filtered_words = [w for w in words if w not in self.stopwords]
        word_counts = Counter(filtered_words)

        # Calculate relevance (simple TF-IDF-like metric)
        total_words = len(filtered_words)
        keywords = []

        for word, count in word_counts.most_common(50):
            relevance = count / total_words * 100  # Percentage
            keywords.append({
                'word': word,
                'count': count,
                'relevance': round(relevance, 2)
            })

        # Group similar keywords as topics
        topic_distribution = {}
        for kw in keywords[:10]:
            topic_distribution[kw['word']] = kw['count']

        return {
            'keywords': keywords,
            'topic_distribution': topic_distribution
        }

    def _analyze_participant_topics(self, conversation: Conversation) -> Dict[str, List[str]]:
        """Analyze topics per participant."""

        participant_topics = {}
        participants = conversation.get_participants_list()

        for participant in participants:
            # Get messages from this participant
            participant_messages = [
                msg for msg in conversation.messages
                if msg.sender == participant
            ]

            if not participant_messages:
                continue

            # Extract keywords
            text = ' '.join([msg.content for msg in participant_messages])
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            filtered_words = [w for w in words if w not in self.stopwords]

            # Get top keywords for this participant
            word_counts = Counter(filtered_words)
            top_keywords = [word for word, count in word_counts.most_common(5)]

            participant_topics[participant] = top_keywords

        return participant_topics
