"""
Enhanced Content Analyzer - Advanced AI-powered content analysis.

Analyzes conversation content for:
- Hate speech and toxicity
- Statement types (questions, commands, assertions)
- Emotional intensity
- Urgency detection
- Language complexity
"""

import os
from typing import Dict, Any, List, Optional
from collections import Counter
import re
import logging

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from .base_analyzer import BaseAnalyzer
from .groq_model_manager import GroqModelManager, AnalysisTask
from ..models import Conversation


class ContentAnalyzer(BaseAnalyzer):
    """
    Analyze conversation content with advanced AI.

    Provides insights into content safety, communication styles,
    and conversation dynamics.
    """

    def __init__(self, api_key: Optional[str] = None, use_ai: bool = True):
        """
        Initialize content analyzer.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            use_ai: Whether to use AI analysis
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.use_ai = use_ai and HAS_GROQ and self.api_key
        self.model_manager = GroqModelManager()

        if self.use_ai:
            self.client = Groq(api_key=self.api_key)

        # Keyword patterns for non-AI analysis
        self.urgency_keywords = {
            'urgent', 'asap', 'emergency', 'immediately', 'right now', 'hurry',
            'critical', 'important', 'priority', 'quickly', 'fast', '!!!', '!!',
            'now', 'today', 'tonight'
        }

        self.question_patterns = [
            r'\?$',  # Ends with ?
            r'^(what|when|where|why|who|how|which|can|could|would|should|is|are|do|does|did)',
        ]

        self.command_patterns = [
            r'^(please|pls|go|come|send|give|show|tell|let|make|do|stop|start)',
        ]

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze conversation content.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dict with content analysis:
            {
                'hate_speech_analysis': Dict,
                'statement_types': Dict,
                'emotional_intensity': Dict,
                'urgency_analysis': Dict,
                'language_complexity': Dict,
                'communication_dynamics': Dict
            }
        """
        self._validate_conversation(conversation)

        results = {}

        # Hate speech analysis
        results['hate_speech_analysis'] = self._analyze_hate_speech(conversation)

        # Statement types
        results['statement_types'] = self._analyze_statement_types(conversation)

        # Emotional intensity
        results['emotional_intensity'] = self._analyze_emotional_intensity(conversation)

        # Urgency detection
        results['urgency_analysis'] = self._analyze_urgency(conversation)

        # Language complexity
        results['language_complexity'] = self._analyze_language_complexity(conversation)

        # Communication dynamics
        results['communication_dynamics'] = self._analyze_communication_dynamics(conversation)

        return results

    def _analyze_hate_speech(self, conversation: Conversation) -> Dict[str, Any]:
        """Detect hate speech, toxicity, and harmful content."""
        if not self.use_ai:
            return {'method': 'keyword', 'note': 'AI analysis not available'}

        # Sample messages for analysis (use first 50 to avoid token limits)
        sample_messages = conversation.messages[:50]

        if not sample_messages:
            return {}

        # Build prompt for hate speech detection
        messages_text = "\n".join([
            f"{i+1}. [{msg.sender}]: {msg.content[:200]}"
            for i, msg in enumerate(sample_messages)
        ])

        # Use best reasoning model for hate speech detection
        model = self.model_manager.select_model(AnalysisTask.HATE_SPEECH)

        prompt = f"""Analyze this conversation for harmful content. Look for:
- Hate speech (racism, sexism, homophobia, etc.)
- Threats or violence
- Harassment or bullying
- Toxic language
- Offensive slurs

Conversation ({len(sample_messages)} messages):
{messages_text}

Respond in JSON format:
{{
  "overall_toxicity": "none/low/medium/high",
  "issues_found": ["list of specific issues, if any"],
  "flagged_message_numbers": [list of message numbers with issues],
  "safety_score": 0-100,
  "summary": "brief summary"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON response
            import json
            result = json.loads(result_text)
            result['method'] = 'ai'
            result['model'] = model
            result['messages_analyzed'] = len(sample_messages)

            return result

        except Exception as e:
            self.logger.error(f"Hate speech analysis failed: {e}")
            return {
                'error': str(e),
                'method': 'ai',
                'overall_toxicity': 'unknown'
            }

    def _analyze_statement_types(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze types of statements (questions, commands, assertions)."""
        statement_counts = {
            'questions': 0,
            'commands': 0,
            'assertions': 0,
            'exclamations': 0
        }

        for msg in conversation.messages:
            content = msg.content.strip().lower()

            # Check for questions
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in self.question_patterns):
                statement_counts['questions'] += 1
            # Check for commands
            elif any(re.search(pattern, content, re.IGNORECASE) for pattern in self.command_patterns):
                statement_counts['commands'] += 1
            # Check for exclamations
            elif content.count('!') >= 2:
                statement_counts['exclamations'] += 1
            # Default to assertion
            else:
                statement_counts['assertions'] += 1

        total = sum(statement_counts.values())
        percentages = {
            key: round(count / total * 100, 1) if total > 0 else 0
            for key, count in statement_counts.items()
        }

        return {
            'counts': statement_counts,
            'percentages': percentages,
            'total_analyzed': total,
            'dominant_type': max(statement_counts, key=statement_counts.get)
        }

    def _analyze_emotional_intensity(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze emotional intensity of messages."""
        intensity_indicators = {
            'high': 0,    # Multiple exclamation marks, caps
            'medium': 0,  # Some emphasis
            'low': 0      # Neutral
        }

        for msg in conversation.messages:
            content = msg.content

            # High intensity indicators
            if content.count('!') >= 2 or content.count('?') >= 2:
                intensity_indicators['high'] += 1
            elif content.isupper() and len(content) > 10:
                intensity_indicators['high'] += 1
            # Medium intensity
            elif '!' in content or '?' in content:
                intensity_indicators['medium'] += 1
            # Low intensity
            else:
                intensity_indicators['low'] += 1

        total = sum(intensity_indicators.values())
        percentages = {
            key: round(count / total * 100, 1) if total > 0 else 0
            for key, count in intensity_indicators.items()
        }

        return {
            'intensity_distribution': intensity_indicators,
            'percentages': percentages,
            'average_intensity': self._calculate_average_intensity(percentages)
        }

    def _calculate_average_intensity(self, percentages: Dict[str, float]) -> str:
        """Calculate average emotional intensity."""
        score = (percentages['high'] * 3 + percentages['medium'] * 2 + percentages['low'] * 1) / 100

        if score > 2.5:
            return 'high'
        elif score > 1.5:
            return 'medium'
        else:
            return 'low'

    def _analyze_urgency(self, conversation: Conversation) -> Dict[str, Any]:
        """Detect urgent or time-sensitive messages."""
        urgent_messages = []
        urgency_count = 0

        for i, msg in enumerate(conversation.messages):
            content = msg.content.lower()

            # Check for urgency keywords
            if any(keyword in content for keyword in self.urgency_keywords):
                urgency_count += 1
                urgent_messages.append({
                    'message_number': i + 1,
                    'sender': msg.sender,
                    'content': msg.content[:100],
                    'timestamp': msg.timestamp.isoformat()
                })

        total = len(conversation.messages)
        urgency_percentage = round(urgency_count / total * 100, 1) if total > 0 else 0

        return {
            'urgent_message_count': urgency_count,
            'total_messages': total,
            'urgency_percentage': urgency_percentage,
            'urgent_messages': urgent_messages[:10],  # Top 10
            'has_urgent_content': urgency_count > 0
        }

    def _analyze_language_complexity(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze language complexity and vocabulary."""
        total_words = 0
        total_sentences = 0
        total_chars = 0
        all_words = []

        for msg in conversation.messages:
            content = msg.content

            # Count words
            words = content.split()
            total_words += len(words)
            all_words.extend(words)

            # Count sentences (rough estimate)
            sentences = content.count('.') + content.count('!') + content.count('?')
            total_sentences += max(sentences, 1)  # At least 1 sentence per message

            # Count characters
            total_chars += len(content)

        avg_word_length = total_chars / total_words if total_words > 0 else 0
        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0

        # Calculate reading level (rough Flesch-Kincaid approximation)
        reading_level = 0.39 * avg_sentence_length + 11.8 * (total_chars / total_words) - 15.59 if total_words > 0 else 0
        reading_level = max(0, round(reading_level, 1))

        return {
            'average_word_length': round(avg_word_length, 2),
            'average_sentence_length': round(avg_sentence_length, 2),
            'estimated_reading_level': reading_level,
            'complexity_rating': self._rate_complexity(reading_level),
            'total_words': total_words,
            'total_sentences': total_sentences
        }

    def _rate_complexity(self, reading_level: float) -> str:
        """Rate language complexity."""
        if reading_level < 6:
            return 'simple'
        elif reading_level < 10:
            return 'moderate'
        elif reading_level < 14:
            return 'complex'
        else:
            return 'very_complex'

    def _analyze_communication_dynamics(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze who initiates conversations and response patterns."""
        participants = conversation.get_participants_list()

        if len(participants) < 2:
            return {'note': 'Single participant conversation'}

        # Track who starts conversations (after gaps)
        initiations = Counter()
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        if len(messages) < 2:
            return {}

        # First message is an initiation
        initiations[messages[0].sender] += 1

        # Check for initiations after 1-hour gaps
        for i in range(1, len(messages)):
            time_gap = (messages[i].timestamp - messages[i-1].timestamp).total_seconds() / 3600

            if time_gap >= 1:  # 1 hour gap = new conversation
                initiations[messages[i].sender] += 1

        # Calculate response patterns
        response_counts = Counter()
        for i in range(1, len(messages)):
            if messages[i].sender != messages[i-1].sender:
                response_counts[messages[i].sender] += 1

        return {
            'conversation_initiations': dict(initiations),
            'response_counts': dict(response_counts),
            'most_likely_initiator': initiations.most_common(1)[0][0] if initiations else None,
            'most_responsive': response_counts.most_common(1)[0][0] if response_counts else None
        }
