"""
Analytics Engine - Orchestrates all analytics modules.

Runs all analyzers and aggregates results into comprehensive
conversation insights.
"""

import time
from typing import Dict, Any, Optional, List
import logging

from .sentiment_analyzer import SentimentAnalyzer
from .topic_analyzer import TopicAnalyzer
from .word_frequency import WordFrequencyAnalyzer
from .activity_analyzer import ActivityAnalyzer
from .call_log_analyzer import CallLogAnalyzer
from .content_analyzer import ContentAnalyzer
from .network_analyzer import NetworkGraphAnalyzer
from ..models import Conversation


class AnalyticsEngine:
    """
    Main analytics engine that runs all analyzers.

    Provides comprehensive conversation insights including sentiment,
    topics, word frequency, and activity patterns.
    """

    def __init__(self, groq_api_key: Optional[str] = None, use_ai: bool = True, use_ensemble: bool = False):
        """
        Initialize analytics engine.

        Args:
            groq_api_key: Groq API key for AI-powered analysis
            use_ai: Whether to use AI analysis (requires API key)
            use_ensemble: Use ensemble sentiment analysis (VADER + TextBlob + Keywords)
        """
        self.logger = logging.getLogger(__name__)
        self.use_ai = use_ai
        self.use_ensemble = use_ensemble

        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer(api_key=groq_api_key, use_ai=use_ai, use_ensemble=use_ensemble)
        self.topic_analyzer = TopicAnalyzer(api_key=groq_api_key, use_ai=use_ai)
        self.word_frequency_analyzer = WordFrequencyAnalyzer()
        self.activity_analyzer = ActivityAnalyzer()
        self.call_log_analyzer = CallLogAnalyzer()
        self.content_analyzer = ContentAnalyzer(api_key=groq_api_key, use_ai=use_ai)
        self.network_analyzer = NetworkGraphAnalyzer()

    def analyze(
        self,
        conversation: Conversation,
        analyzers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive analysis on conversation.

        Args:
            conversation: Conversation to analyze
            analyzers: Optional list of specific analyzers to run.
                      Options: ['sentiment', 'topics', 'word_frequency', 'activity']
                      If None, runs all analyzers.

        Returns:
            Dict with complete analysis results:
            {
                'conversation_info': Dict,
                'sentiment': Dict,
                'topics': Dict,
                'word_frequency': Dict,
                'activity': Dict,
                'summary': Dict,
                'processing_time': float
            }
        """
        start_time = time.time()

        if analyzers is None:
            analyzers = ['sentiment', 'topics', 'word_frequency', 'activity']

        self.logger.info(f"Running analysis with: {', '.join(analyzers)}")

        results = {
            'conversation_info': self._get_conversation_info(conversation)
        }

        # Auto-detect and run call log analysis
        try:
            self.logger.info("Checking if conversation is a call log...")
            call_log_results = self.call_log_analyzer.analyze(conversation)
            results['call_log'] = call_log_results

            # If this is a call log, skip sentiment and topic analysis
            # (they don't make sense for call logs)
            if call_log_results.get('is_call_log'):
                self.logger.info("Call log detected! Running call-specific analytics...")
                analyzers = ['word_frequency', 'activity']  # Only run these for call logs
        except Exception as e:
            self.logger.error(f"Call log analysis failed: {e}")
            results['call_log'] = {'error': str(e)}

        # Run sentiment analysis
        if 'sentiment' in analyzers:
            try:
                self.logger.info("Running sentiment analysis...")
                results['sentiment'] = self.sentiment_analyzer.analyze(conversation)
            except Exception as e:
                self.logger.error(f"Sentiment analysis failed: {e}")
                results['sentiment'] = {'error': str(e)}

        # Run topic analysis
        if 'topics' in analyzers:
            try:
                self.logger.info("Running topic analysis...")
                results['topics'] = self.topic_analyzer.analyze(conversation)
            except Exception as e:
                self.logger.error(f"Topic analysis failed: {e}")
                results['topics'] = {'error': str(e)}

        # Run word frequency analysis
        if 'word_frequency' in analyzers:
            try:
                self.logger.info("Running word frequency analysis...")
                results['word_frequency'] = self.word_frequency_analyzer.analyze(conversation)
            except Exception as e:
                self.logger.error(f"Word frequency analysis failed: {e}")
                results['word_frequency'] = {'error': str(e)}

        # Run activity analysis
        if 'activity' in analyzers:
            try:
                self.logger.info("Running activity analysis...")
                results['activity'] = self.activity_analyzer.analyze(conversation)
            except Exception as e:
                self.logger.error(f"Activity analysis failed: {e}")
                results['activity'] = {'error': str(e)}

        # Run enhanced content analysis (not for call logs)
        if not results.get('call_log', {}).get('is_call_log') and self.use_ai:
            try:
                self.logger.info("Running enhanced content analysis...")
                results['content_analysis'] = self.content_analyzer.analyze(conversation)
            except Exception as e:
                self.logger.error(f"Content analysis failed: {e}")
                results['content_analysis'] = {'error': str(e)}

        # Run network graph analysis (if multiple participants)
        if len(conversation.get_participants_list()) > 1:
            try:
                self.logger.info("Running network graph analysis...")
                results['network_graph'] = self.network_analyzer.analyze(conversation)
            except Exception as e:
                self.logger.error(f"Network graph analysis failed: {e}")
                results['network_graph'] = {'error': str(e), 'available': False}

        # Generate summary
        results['summary'] = self._generate_summary(results)

        processing_time = time.time() - start_time
        results['processing_time'] = round(processing_time, 3)

        self.logger.info(f"Analysis complete in {processing_time:.2f}s")

        return results

    def _get_conversation_info(self, conversation: Conversation) -> Dict[str, Any]:
        """Get basic conversation information."""
        return {
            'id': conversation.id,
            'title': conversation.title,
            'platform': conversation.platform,
            'type': conversation.conversation_type,
            'total_messages': len(conversation.messages),
            'total_participants': len(conversation.participants),
            'participants': conversation.get_participants_list()
        }

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of analysis results."""
        summary = {}

        # Call log summary
        if 'call_log' in results and 'error' not in results['call_log']:
            call_data = results['call_log']
            if call_data.get('is_call_log'):
                summary['call_log'] = {
                    'is_call_log': True,
                    'total_calls': call_data.get('total_calls'),
                    'missed_calls': call_data.get('missed_calls'),
                    'total_duration_minutes': call_data.get('total_duration_minutes'),
                    'top_contact': call_data.get('calls_by_contact', [{}])[0].get('contact', 'N/A') if call_data.get('calls_by_contact') else 'N/A'
                }

        # Sentiment summary
        if 'sentiment' in results and 'error' not in results['sentiment']:
            sentiment_data = results['sentiment']
            summary['sentiment'] = {
                'overall': sentiment_data.get('overall_sentiment'),
                'score': sentiment_data.get('sentiment_score'),
                'distribution': sentiment_data.get('sentiment_distribution')
            }

        # Topic summary
        if 'topics' in results and 'error' not in results['topics']:
            topic_data = results['topics']
            summary['topics'] = {
                'main_topics': topic_data.get('main_topics', [])[:5],
                'top_keywords': [
                    kw['word'] for kw in topic_data.get('keywords', [])[:10]
                ]
            }

        # Activity summary
        if 'activity' in results and 'error' not in results['activity']:
            activity_data = results['activity']
            summary['activity'] = {
                'total_messages': activity_data.get('total_messages'),
                'busiest_day': activity_data.get('busiest_day'),
                'most_active_participant': activity_data.get('most_active_participant', {}).get('name')
            }

        # Word stats summary
        if 'word_frequency' in results and 'error' not in results['word_frequency']:
            word_data = results['word_frequency']
            summary['word_stats'] = {
                'total_words': word_data.get('total_words'),
                'unique_words': word_data.get('unique_words'),
                'vocabulary_diversity': word_data.get('vocabulary_diversity')
            }

        return summary

    def generate_report(self, conversation: Conversation) -> str:
        """
        Generate human-readable text report of analysis.

        Args:
            conversation: Conversation to analyze

        Returns:
            Formatted text report
        """
        results = self.analyze(conversation)

        report = []
        report.append("="*60)
        report.append(f"CONVERSATION ANALYTICS REPORT")
        report.append("="*60)
        report.append("")

        # Conversation Info
        info = results['conversation_info']
        report.append(f"Title: {info['title']}")
        report.append(f"Platform: {info['platform']}")
        report.append(f"Messages: {info['total_messages']}")
        report.append(f"Participants: {', '.join(info['participants'])}")
        report.append("")

        # Call Log Analysis (if detected)
        if 'call_log' in results and 'error' not in results['call_log']:
            call_data = results['call_log']
            if call_data.get('is_call_log'):
                report.append("CALL LOG DETECTED")
                report.append("-"*60)
                report.append(f"Total Calls: {call_data.get('total_calls')}")
                report.append(f"Completed Calls: {call_data.get('completed_calls')}")
                report.append(f"Missed Calls: {call_data.get('missed_calls')} ({call_data.get('missed_call_percentage')}%)")
                report.append(f"Total Talk Time: {call_data.get('total_duration_minutes')} minutes")
                report.append(f"Average Call Duration: {call_data.get('average_duration_minutes')} minutes")

                direction = call_data.get('incoming_vs_outgoing', {})
                report.append(f"Incoming: {direction.get('incoming')} ({direction.get('incoming_percentage')}%)")
                report.append(f"Outgoing: {direction.get('outgoing')} ({direction.get('outgoing_percentage')}%)")

                # Top contacts
                if call_data.get('calls_by_contact'):
                    report.append("")
                    report.append("Top 3 Contacts:")
                    for i, contact in enumerate(call_data['calls_by_contact'][:3], 1):
                        report.append(f"  {i}. {contact['contact']}: {contact['call_count']} calls")

                # Peak time
                if call_data.get('peak_calling_time'):
                    peak = call_data['peak_calling_time']
                    report.append(f"Peak Time: {peak['time_range']} ({peak['call_count']} calls)")

                report.append("")

        # Sentiment
        if 'sentiment' in results and 'error' not in results['sentiment']:
            sentiment = results['sentiment']
            report.append("SENTIMENT ANALYSIS")
            report.append("-"*60)
            report.append(f"Overall Sentiment: {sentiment['overall_sentiment'].upper()}")
            report.append(f"Sentiment Score: {sentiment['sentiment_score']:.2f} (-1 to 1)")
            report.append(f"Distribution: {sentiment['sentiment_distribution']}")
            report.append(f"Analysis Method: {sentiment['method'].upper()}")
            report.append("")

        # Topics
        if 'topics' in results and 'error' not in results['topics']:
            topics = results['topics']
            report.append("TOPIC ANALYSIS")
            report.append("-"*60)
            report.append("Main Topics:")
            for i, topic in enumerate(topics['main_topics'][:5], 1):
                report.append(f"  {i}. {topic}")
            report.append("")
            report.append("Top Keywords:")
            for kw in topics['keywords'][:10]:
                report.append(f"  • {kw['word']} ({kw['count']} times)")
            report.append("")

        # Activity
        if 'activity' in results and 'error' not in results['activity']:
            activity = results['activity']
            report.append("ACTIVITY ANALYSIS")
            report.append("-"*60)
            most_active = activity.get('most_active_participant', {})
            if most_active.get('name'):
                report.append(f"Most Active: {most_active['name']} ({most_active.get('message_count', 0)} messages)")
            busiest = activity.get('busiest_day', {})
            if busiest:
                report.append(f"Busiest Day: {busiest.get('date')} ({busiest.get('count', 0)} messages)")
            report.append(f"Busiest Hour: {activity.get('busiest_hour')}:00")
            report.append("")

        # Word Frequency
        if 'word_frequency' in results and 'error' not in results['word_frequency']:
            words = results['word_frequency']
            report.append("WORD STATISTICS")
            report.append("-"*60)
            report.append(f"Total Words: {words['total_words']:,}")
            report.append(f"Unique Words: {words['unique_words']:,}")
            report.append(f"Vocabulary Diversity: {words['vocabulary_diversity']:.1%}")
            report.append("")

        report.append("="*60)
        report.append(f"Analysis completed in {results['processing_time']:.2f}s")
        report.append("="*60)

        return "\n".join(report)
