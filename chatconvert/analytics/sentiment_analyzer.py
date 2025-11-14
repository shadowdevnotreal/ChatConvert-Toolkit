"""
Sentiment Analyzer using multiple methods.

Analyzes sentiment of messages using:
1. VADER (Valence Aware Dictionary and sEntiment Reasoner) - best for social media
2. Groq AI - advanced LLM-based analysis
3. Keyword-based - fallback when other methods unavailable

VADER is recommended for chat/social media text as it handles:
- Informal language and slang
- Emojis and emoticons
- ALL CAPS (shouting)
- Punctuation intensity (!!! ???)
- Negation and contractions
"""

import os
from typing import Dict, Any, List, Optional
from collections import Counter

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
except ImportError:
    HAS_VADER = False

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

from .base_analyzer import BaseAnalyzer
from .groq_model_manager import GroqModelManager, AnalysisTask
from ..models import Conversation


class SentimentAnalyzer(BaseAnalyzer):
    """Analyze sentiment of conversation messages using multiple methods."""

    def __init__(self, api_key: Optional[str] = None, use_ai: bool = True, use_ensemble: bool = False):
        """
        Initialize sentiment analyzer.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            use_ai: Whether to use AI analysis (fallback to VADER or keywords)
            use_ensemble: Use ensemble method (combines VADER + TextBlob + Keywords)
        """
        super().__init__()
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.use_ai = use_ai and HAS_GROQ and self.api_key
        self.use_ensemble = use_ensemble
        self.model_manager = GroqModelManager()

        # Initialize VADER if available
        if HAS_VADER:
            self.vader = SentimentIntensityAnalyzer()
            self.logger.info("VADER sentiment analyzer initialized")
        else:
            self.vader = None
            self.logger.info("VADER not available")

        # Initialize TextBlob (always available, part of Python)
        self.textblob_available = HAS_TEXTBLOB
        if HAS_TEXTBLOB:
            self.logger.info("TextBlob sentiment analyzer initialized")
        else:
            self.logger.info("TextBlob not available")

        if self.use_ai:
            self.client = Groq(api_key=self.api_key)
            # Use model manager to select best model for sentiment analysis
            self.model = self.model_manager.select_model(AnalysisTask.SENTIMENT, priority_speed=True)

        # Keyword-based fallback with expanded wordlists
        self.positive_words = {
            'good', 'great', 'awesome', 'excellent', 'happy', 'love', 'wonderful',
            'amazing', 'fantastic', 'perfect', 'best', 'brilliant', 'nice', 'cool',
            'thanks', 'thank', 'appreciate', 'beautiful', 'lovely', 'sweet', 'kind',
            'joy', 'pleased', 'excited', 'thrilled', 'delighted', 'glad', 'blessed',
            'fantastic', 'superb', 'outstanding', 'marvelous', 'terrific',
            '😊', '❤️', '👍', '😄', '🎉', '🥰', '😍', '🙏', '✨'
        }

        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor',
            'disappointing', 'sad', 'angry', 'annoying', 'frustrated', 'sorry',
            'wrong', 'problem', 'issue', 'sucks', 'stupid', 'dumb', 'idiot',
            'pathetic', 'useless', 'worthless', 'disgusting', 'sick', 'cruel',
            'mean', 'rude', 'nasty', 'vile', 'evil', 'ugly', 'trash', 'garbage',
            '😢', '😠', '👎', '😞', '💔', '😡', '🤬'
        }

        # Severe/abusive language (weighted more heavily)
        self.severe_words = {
            'abuse', 'abused', 'abuser', 'abusive', 'assault', 'assaulted',
            'attack', 'attacked', 'attacking', 'violence', 'violent', 'violate',
            'violated', 'violating', 'rape', 'raped', 'raping', 'molest', 'harass',
            'harassment', 'threat', 'threaten', 'threatened', 'threatening',
            'kill', 'murder', 'die', 'death', 'hurt', 'harm', 'damage', 'destroy',
            'torture', 'torment', 'terrorize', 'stalk', 'stalking', 'predator',
            'victim', 'trauma', 'traumatic', 'danger', 'dangerous', 'weapon'
        }

        # Profanity (also weighted heavily)
        self.profanity = {
            'fuck', 'fucking', 'fucked', 'shit', 'shitty', 'damn', 'damned',
            'hell', 'bastard', 'bitch', 'ass', 'asshole', 'crap', 'piss'
        }

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze sentiment of all messages in conversation.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dict with sentiment analysis results:
            {
                'overall_sentiment': str,  # 'positive', 'negative', 'neutral'
                'sentiment_score': float,  # -1.0 to 1.0
                'message_sentiments': List[Dict],
                'participant_sentiments': Dict[str, Dict],
                'sentiment_distribution': Dict[str, int],
                'method': str,  # 'ai', 'vader', 'textblob', 'ensemble', or 'keyword'
                'polarity': float,  # TextBlob polarity (if available)
                'subjectivity': float  # TextBlob subjectivity (if available)
            }
        """
        self._validate_conversation(conversation)

        # Priority: Ensemble > AI > VADER > TextBlob > Keywords
        if self.use_ensemble and (self.vader or self.textblob_available):
            return self._analyze_with_ensemble(conversation)
        elif self.use_ai:
            return self._analyze_with_ai(conversation)
        elif self.vader:
            return self._analyze_with_vader(conversation)
        elif self.textblob_available:
            return self._analyze_with_textblob(conversation)
        else:
            return self._analyze_with_keywords(conversation)

    def _analyze_with_ai(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze using Groq AI."""
        self.logger.info("Analyzing sentiment with Groq AI")

        message_sentiments = []

        # Analyze messages in batches to reduce API calls
        batch_size = 10
        messages = conversation.messages

        for i in range(0, len(messages), batch_size):
            batch = messages[i:i+batch_size]

            # Create prompt
            messages_text = "\n".join([
                f"{j+1}. [{msg.sender}]: {msg.content}"
                for j, msg in enumerate(batch)
            ])

            prompt = f"""Analyze the sentiment of these chat messages.
For each message, respond with ONLY a number from -1 to 1:
-1 = very negative
0 = neutral
1 = very positive

Messages:
{messages_text}

Respond with ONLY the numbers, one per line, no explanation:"""

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=100
                )

                # Parse scores
                scores_text = response.choices[0].message.content.strip()
                scores = []
                for line in scores_text.split('\n'):
                    try:
                        score = float(line.strip())
                        scores.append(max(-1.0, min(1.0, score)))  # Clamp to range
                    except ValueError:
                        scores.append(0.0)  # Default to neutral

                # Map scores to messages
                for j, msg in enumerate(batch):
                    score = scores[j] if j < len(scores) else 0.0
                    sentiment = 'positive' if score > 0.2 else 'negative' if score < -0.2 else 'neutral'

                    message_sentiments.append({
                        'message_id': msg.id,
                        'sender': msg.sender,
                        'content': msg.content[:100],
                        'sentiment': sentiment,
                        'score': score
                    })

            except Exception as e:
                self.logger.warning(f"AI analysis failed for batch: {e}")
                # Fallback to keyword analysis for this batch
                for msg in batch:
                    score = self._keyword_score(msg.content)
                    sentiment = 'positive' if score > 0.2 else 'negative' if score < -0.2 else 'neutral'
                    message_sentiments.append({
                        'message_id': msg.id,
                        'sender': msg.sender,
                        'content': msg.content[:100],
                        'sentiment': sentiment,
                        'score': score
                    })

        return self._aggregate_results(conversation, message_sentiments, 'ai')

    def _analyze_with_vader(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze using VADER (Valence Aware Dictionary and sEntiment Reasoner).

        VADER is specifically designed for social media text and handles:
        - Informal language, slang, abbreviations
        - Emojis and emoticons
        - ALL CAPS (shouting/emphasis)
        - Punctuation intensity (!!!, ???)
        - Negation and contractions
        - Degree modifiers (very, extremely, etc.)
        """
        self.logger.info("Analyzing sentiment with VADER")

        message_sentiments = []

        for msg in conversation.messages:
            # Handle null/empty messages
            if not msg.content or not msg.content.strip():
                message_sentiments.append({
                    'message_id': msg.id,
                    'sender': msg.sender,
                    'content': '',
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'vader_scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
                })
                continue

            # VADER returns compound score (-1 to 1) and pos/neg/neu scores
            scores = self.vader.polarity_scores(msg.content)

            # Use compound score as overall sentiment
            # VADER recommends: compound >= 0.05 = positive, <= -0.05 = negative, else neutral
            compound = scores['compound']

            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            message_sentiments.append({
                'message_id': msg.id,
                'sender': msg.sender,
                'content': msg.content[:100],
                'sentiment': sentiment,
                'score': compound,
                'vader_scores': {
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu']
                }
            })

        return self._aggregate_results(conversation, message_sentiments, 'vader')

    def _analyze_with_textblob(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze using TextBlob.

        TextBlob provides:
        - Polarity: -1.0 (negative) to 1.0 (positive)
        - Subjectivity: 0.0 (objective) to 1.0 (subjective)

        Good for: Basic sentiment analysis, opinion mining, polarity scoring
        """
        self.logger.info("Analyzing sentiment with TextBlob")

        message_sentiments = []
        all_polarity = []
        all_subjectivity = []

        for msg in conversation.messages:
            # Handle null/empty messages
            if not msg.content or not msg.content.strip():
                message_sentiments.append({
                    'message_id': msg.id,
                    'sender': msg.sender,
                    'content': '',
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'polarity': 0.0,
                    'subjectivity': 0.0
                })
                continue

            # Get TextBlob analysis
            blob = TextBlob(msg.content)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            all_polarity.append(polarity)
            all_subjectivity.append(subjectivity)

            # Classify sentiment based on polarity
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            message_sentiments.append({
                'message_id': msg.id,
                'sender': msg.sender,
                'content': msg.content[:100],
                'sentiment': sentiment,
                'score': polarity,
                'polarity': polarity,
                'subjectivity': subjectivity
            })

        # Add average polarity/subjectivity to results
        results = self._aggregate_results(conversation, message_sentiments, 'textblob')
        if all_polarity:
            results['avg_polarity'] = sum(all_polarity) / len(all_polarity)
            results['avg_subjectivity'] = sum(all_subjectivity) / len(all_subjectivity)

        return results

    def _analyze_with_ensemble(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Ensemble method: Combines VADER, TextBlob, and Keywords for better accuracy.

        Weighted average:
        - VADER: 50% (best for social media)
        - TextBlob: 30% (good for polarity)
        - Keywords: 20% (fallback)

        This reduces false positives/negatives by combining multiple approaches.
        """
        self.logger.info("Analyzing sentiment with ensemble method (VADER + TextBlob + Keywords)")

        message_sentiments = []

        for msg in conversation.messages:
            # Handle null/empty messages
            if not msg.content or not msg.content.strip():
                message_sentiments.append({
                    'message_id': msg.id,
                    'sender': msg.sender,
                    'content': '',
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'ensemble_scores': {}
                })
                continue

            scores = {}
            weights = {}

            # Get VADER score (if available)
            if self.vader:
                vader_scores = self.vader.polarity_scores(msg.content)
                scores['vader'] = vader_scores['compound']
                weights['vader'] = 0.5

            # Get TextBlob score (if available)
            if self.textblob_available:
                blob = TextBlob(msg.content)
                scores['textblob'] = blob.sentiment.polarity
                weights['textblob'] = 0.3

            # Get keyword score (always available)
            scores['keywords'] = self._keyword_score(msg.content)
            weights['keywords'] = 0.2

            # Normalize weights if some methods unavailable
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v / total_weight for k, v in weights.items()}

            # Calculate weighted average
            ensemble_score = sum(scores[k] * weights[k] for k in scores.keys())

            # Classify sentiment
            if ensemble_score > 0.1:
                sentiment = 'positive'
            elif ensemble_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            message_sentiments.append({
                'message_id': msg.id,
                'sender': msg.sender,
                'content': msg.content[:100],
                'sentiment': sentiment,
                'score': ensemble_score,
                'ensemble_scores': scores,
                'ensemble_weights': weights
            })

        return self._aggregate_results(conversation, message_sentiments, 'ensemble')

    def _analyze_with_keywords(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze using keyword-based approach (fallback when VADER/AI unavailable)."""
        self.logger.info("Analyzing sentiment with keywords")

        message_sentiments = []

        for msg in conversation.messages:
            # Handle null/empty messages
            if not msg.content or not msg.content.strip():
                message_sentiments.append({
                    'message_id': msg.id,
                    'sender': msg.sender,
                    'content': '',
                    'sentiment': 'neutral',
                    'score': 0.0
                })
                continue

            score = self._keyword_score(msg.content)
            sentiment = 'positive' if score > 0.2 else 'negative' if score < -0.2 else 'neutral'

            message_sentiments.append({
                'message_id': msg.id,
                'sender': msg.sender,
                'content': msg.content[:100],
                'sentiment': sentiment,
                'score': score
            })

        return self._aggregate_results(conversation, message_sentiments, 'keyword')

    def _keyword_score(self, text: str) -> float:
        """Calculate sentiment score based on keywords with enhanced detection."""
        text_lower = text.lower()
        words = set(text_lower.split())

        positive_count = len(words & self.positive_words)
        negative_count = len(words & self.negative_words)

        # Severe/abusive language (count with 3x weight)
        severe_count = len(words & self.severe_words) * 3
        negative_count += severe_count

        # Profanity (count with 2x weight)
        profanity_count = len(words & self.profanity) * 2
        negative_count += profanity_count

        # Check for emojis in original text
        for emoji in self.positive_words:
            if emoji in text:
                positive_count += 1
        for emoji in self.negative_words:
            if emoji in text:
                negative_count += 1

        # ALL CAPS detection (shouting = negative)
        # Consider a message as shouting if >70% uppercase and >10 chars
        if len(text.strip()) > 10:
            uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if uppercase_ratio > 0.7:
                negative_count += 3  # Heavy penalty for shouting

        # Multiple exclamation marks (emotional intensity)
        exclamation_count = text.count('!')
        if exclamation_count > 2:
            # If combined with negative words, make it more negative
            if negative_count > positive_count:
                negative_count += exclamation_count // 2
            else:
                positive_count += exclamation_count // 3  # Could be excitement

        # Multiple question marks (concern/confusion = slightly negative)
        question_count = text.count('?')
        if question_count > 2:
            negative_count += question_count // 3

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        score = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, score))

    def _aggregate_results(
        self,
        conversation: Conversation,
        message_sentiments: List[Dict],
        method: str
    ) -> Dict[str, Any]:
        """Aggregate sentiment results."""

        # Overall sentiment
        avg_score = sum(m['score'] for m in message_sentiments) / len(message_sentiments)
        overall = 'positive' if avg_score > 0.2 else 'negative' if avg_score < -0.2 else 'neutral'

        # Sentiment distribution
        sentiment_counts = Counter(m['sentiment'] for m in message_sentiments)

        # Per-participant sentiment
        participant_sentiments = {}
        participants = conversation.get_participants_list()

        for participant in participants:
            participant_messages = [
                m for m in message_sentiments if m['sender'] == participant
            ]
            if participant_messages:
                avg = sum(m['score'] for m in participant_messages) / len(participant_messages)
                sentiment = 'positive' if avg > 0.2 else 'negative' if avg < -0.2 else 'neutral'

                participant_sentiments[participant] = {
                    'sentiment': sentiment,
                    'score': avg,
                    'message_count': len(participant_messages),
                    'positive': sum(1 for m in participant_messages if m['sentiment'] == 'positive'),
                    'neutral': sum(1 for m in participant_messages if m['sentiment'] == 'neutral'),
                    'negative': sum(1 for m in participant_messages if m['sentiment'] == 'negative'),
                }

        # Score distribution for validation (recommended by best practices)
        score_ranges = {
            'very_negative': sum(1 for m in message_sentiments if m['score'] <= -0.6),
            'negative': sum(1 for m in message_sentiments if -0.6 < m['score'] <= -0.2),
            'neutral': sum(1 for m in message_sentiments if -0.2 < m['score'] < 0.2),
            'positive': sum(1 for m in message_sentiments if 0.2 <= m['score'] < 0.6),
            'very_positive': sum(1 for m in message_sentiments if m['score'] >= 0.6)
        }

        return {
            'overall_sentiment': overall,
            'sentiment_score': avg_score,
            'message_sentiments': message_sentiments,
            'participant_sentiments': participant_sentiments,
            'sentiment_distribution': dict(sentiment_counts),
            'score_distribution': score_ranges,  # For validation visualization
            'method': method,
            'total_messages': len(message_sentiments)
        }
