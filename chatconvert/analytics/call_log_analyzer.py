"""
Call Log Analyzer - Specialized analytics for call logs.

Detects call logs and provides call-specific insights like duration patterns,
missed calls, peak calling times, and most frequent contacts.
"""

import re
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from datetime import datetime
import logging

from ..models import Conversation, Message, MessageType


class CallLogAnalyzer:
    """
    Analyze call logs with specialized metrics.

    Provides insights specific to phone calls like duration patterns,
    missed vs completed calls, peak calling times, and contact frequency.
    """

    def __init__(self):
        """Initialize call log analyzer."""
        self.logger = logging.getLogger(__name__)

    def is_call_log(self, conversation: Conversation) -> bool:
        """
        Detect if conversation is a call log vs regular messages.

        Args:
            conversation: Conversation to analyze

        Returns:
            True if this appears to be a call log, False otherwise
        """
        if not conversation.messages:
            return False

        # Check first 10 messages for call indicators
        sample_size = min(10, len(conversation.messages))
        call_indicators = 0

        for msg in conversation.messages[:sample_size]:
            content = msg.content.lower()

            # Look for call-related patterns (phone calls)
            phone_call_patterns = [
                'call duration', 'missed call', '📞', '❌ missed',
                'incoming call', 'outgoing call', 'call from', 'call to'
            ]

            # Look for dispatch/emergency call patterns
            dispatch_patterns = [
                'dispatch', 'arrive', 'terminal', 'event', 'case number',
                'call source', 'loi', 'sector', 'caller phone', 'remarks'
            ]

            if any(indicator in content for indicator in phone_call_patterns + dispatch_patterns):
                call_indicators += 1

        # If more than 30% of sample has call indicators, it's a call log
        return (call_indicators / sample_size) >= 0.3

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze call log patterns and metrics.

        Args:
            conversation: Conversation (call log) to analyze

        Returns:
            Dict with call-specific analytics:
            {
                'is_call_log': bool,
                'total_calls': int,
                'completed_calls': int,
                'missed_calls': int,
                'total_duration_minutes': float,
                'average_duration_minutes': float,
                'longest_call': Dict,
                'shortest_call': Dict,
                'calls_by_contact': List[Dict],
                'calls_by_hour': Dict,
                'calls_by_day': Dict,
                'incoming_vs_outgoing': Dict,
                'peak_calling_time': Dict
            }
        """
        self.logger.info("Running call log analysis...")

        is_call_log = self.is_call_log(conversation)

        if not is_call_log:
            return {
                'is_call_log': False,
                'message': 'This appears to be regular messages, not a call log'
            }

        # Initialize counters
        total_calls = 0
        completed_calls = 0
        missed_calls = 0
        total_duration_seconds = 0
        calls_with_duration = []
        calls_by_contact = defaultdict(lambda: {'count': 0, 'duration': 0, 'missed': 0})
        calls_by_hour = defaultdict(int)
        calls_by_day = defaultdict(int)
        incoming_calls = 0
        outgoing_calls = 0

        # Track structured dispatch data
        dispatch_calls = []
        locations = defaultdict(int)
        call_sources = defaultdict(int)
        event_types = defaultdict(int)
        response_times = []

        # Analyze each call
        for msg in conversation.messages:
            content = msg.content

            # Extract structured fields (dispatch logs)
            struct_fields = self._extract_structured_fields(content)
            if struct_fields:
                dispatch_calls.append({
                    'timestamp': msg.timestamp,
                    'sender': msg.sender,
                    **struct_fields
                })

                # Track locations
                if 'location' in struct_fields:
                    locations[struct_fields['location']] += 1

                # Track call sources
                if 'call_source' in struct_fields:
                    call_sources[struct_fields['call_source']] += 1

                # Track event types
                if 'event_type' in struct_fields:
                    event_types[struct_fields['event_type']] += 1

                # Calculate response time
                response_time = self._calculate_response_time(struct_fields)
                if response_time > 0:
                    response_times.append(response_time)

            # Skip if not a call entry
            if not any(indicator in content.lower() for indicator in ['call', '📞', '❌']):
                continue

            total_calls += 1

            # Extract duration if present
            duration_seconds = self._extract_duration(content)

            # Determine if missed or completed
            if 'missed' in content.lower() or '❌' in content:
                missed_calls += 1
                calls_by_contact[msg.sender]['missed'] += 1
            else:
                completed_calls += 1
                if duration_seconds > 0:
                    total_duration_seconds += duration_seconds
                    calls_with_duration.append({
                        'sender': msg.sender,
                        'duration_seconds': duration_seconds,
                        'duration_formatted': self._format_duration(duration_seconds),
                        'timestamp': msg.timestamp
                    })
                    calls_by_contact[msg.sender]['duration'] += duration_seconds

            # Track by contact
            calls_by_contact[msg.sender]['count'] += 1

            # Track by hour and day
            if msg.timestamp:
                calls_by_hour[msg.timestamp.hour] += 1
                day_name = msg.timestamp.strftime('%A')
                calls_by_day[day_name] += 1

            # Determine direction (incoming vs outgoing)
            if msg.sender == 'Me':
                outgoing_calls += 1
            else:
                incoming_calls += 1

        # Calculate averages and find extremes
        average_duration_seconds = total_duration_seconds / completed_calls if completed_calls > 0 else 0

        longest_call = max(calls_with_duration, key=lambda x: x['duration_seconds']) if calls_with_duration else None
        shortest_call = min(calls_with_duration, key=lambda x: x['duration_seconds']) if calls_with_duration else None

        # Sort contacts by call count
        top_contacts = sorted(
            [
                {
                    'contact': contact,
                    'call_count': data['count'],
                    'total_duration_minutes': round(data['duration'] / 60, 1),
                    'missed_count': data['missed'],
                    'average_duration_minutes': round(data['duration'] / 60 / (data['count'] - data['missed']), 1) if (data['count'] - data['missed']) > 0 else 0
                }
                for contact, data in calls_by_contact.items()
            ],
            key=lambda x: x['call_count'],
            reverse=True
        )

        # Find peak calling hour
        if calls_by_hour:
            peak_hour = max(calls_by_hour.items(), key=lambda x: x[1])
            peak_calling_time = {
                'hour': peak_hour[0],
                'time_range': f"{peak_hour[0]:02d}:00-{peak_hour[0]+1:02d}:00",
                'call_count': peak_hour[1]
            }
        else:
            peak_calling_time = None

        # Find busiest day
        if calls_by_day:
            busiest_day = max(calls_by_day.items(), key=lambda x: x[1])
        else:
            busiest_day = None

        # Dispatch/emergency call analytics
        dispatch_analytics = {}
        if dispatch_calls:
            dispatch_analytics = {
                'total_dispatch_calls': len(dispatch_calls),
                'locations': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]),
                'call_sources': dict(sorted(call_sources.items(), key=lambda x: x[1], reverse=True)),
                'event_types': dict(sorted(event_types.items(), key=lambda x: x[1], reverse=True)),
                'average_response_time_minutes': round(sum(response_times) / len(response_times), 1) if response_times else 0,
                'fastest_response_minutes': min(response_times) if response_times else 0,
                'slowest_response_minutes': max(response_times) if response_times else 0,
                'sample_calls': dispatch_calls[:5]  # First 5 for reference
            }

        return {
            'is_call_log': True,
            'total_calls': total_calls,
            'completed_calls': completed_calls,
            'missed_calls': missed_calls,
            'missed_call_percentage': round((missed_calls / total_calls * 100), 1) if total_calls > 0 else 0,
            'total_duration_minutes': round(total_duration_seconds / 60, 1),
            'average_duration_minutes': round(average_duration_seconds / 60, 1),
            'longest_call': longest_call,
            'shortest_call': shortest_call,
            'calls_by_contact': top_contacts[:10],  # Top 10 contacts
            'calls_by_hour': dict(sorted(calls_by_hour.items())),
            'calls_by_day': dict(calls_by_day),
            'busiest_day': {'day': busiest_day[0], 'count': busiest_day[1]} if busiest_day else None,
            'incoming_calls': incoming_calls,
            'outgoing_calls': outgoing_calls,
            'incoming_vs_outgoing': {
                'incoming': incoming_calls,
                'outgoing': outgoing_calls,
                'incoming_percentage': round((incoming_calls / total_calls * 100), 1) if total_calls > 0 else 0,
                'outgoing_percentage': round((outgoing_calls / total_calls * 100), 1) if total_calls > 0 else 0
            },
            'peak_calling_time': peak_calling_time,
            'dispatch_analytics': dispatch_analytics  # NEW: Structured dispatch data
        }

    def _extract_duration(self, content: str) -> int:
        """
        Extract call duration in seconds from message content.

        Args:
            content: Message content

        Returns:
            Duration in seconds, or 0 if not found
        """
        # Look for patterns like "5m 32s", "32s", "Call duration: 5m 32s"

        # Try minutes and seconds pattern
        match = re.search(r'(\d+)m\s*(\d+)s', content)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds

        # Try seconds only pattern
        match = re.search(r'(\d+)s', content)
        if match:
            return int(match.group(1))

        # Try minutes only pattern
        match = re.search(r'(\d+)m', content)
        if match:
            return int(match.group(1)) * 60

        return 0

    def _format_duration(self, seconds: int) -> str:
        """
        Format duration in human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string like "5m 32s" or "32s"
        """
        if seconds < 60:
            return f"{seconds}s"

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{minutes}m"

    def _extract_structured_fields(self, content: str) -> Dict[str, Any]:
        """
        Extract structured fields from emergency/dispatch call logs.

        Args:
            content: Message content

        Returns:
            Dict with extracted fields
        """
        fields = {}

        # Extract case/event number
        case_patterns = [
            r'case\s*(?:number|#)?\s*:?\s*(\w+[-/]?\w*)',
            r'event\s*(?:number|#)?\s*:?\s*(\w+[-/]?\w*)',
            r'incident\s*(?:number|#)?\s*:?\s*(\w+[-/]?\w*)'
        ]
        for pattern in case_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['case_number'] = match.group(1)
                break

        # Extract location/address
        location_patterns = [
            r'location\s*:?\s*([A-Z][^\n]{10,80})',
            r'address\s*:?\s*([A-Z][^\n]{10,80})',
            r'sector\s*:?\s*([A-Z][^\n]{10,60})',
            r'(?:N|S|E|W)\s+SECTOR\s+([A-Z\s]+)'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields['location'] = match.group(1).strip()
                break

        # Extract phone numbers
        phone_match = re.search(r'(?:caller phone|phone number)\s*:?\s*([\d-]+)', content, re.IGNORECASE)
        if phone_match:
            fields['caller_phone'] = phone_match.group(1)

        # Extract call source codes
        source_match = re.search(r'call source\s*:?\s*([\w-]+)', content, re.IGNORECASE)
        if source_match:
            fields['call_source'] = source_match.group(1)

        # Extract times (dispatch, arrive, close)
        time_fields = {
            'dispatch': r'dispatch\s*(?:time)?\s*:?\s*(\d{1,2}:\d{2})',
            'arrive': r'arrive\s*(?:time)?\s*:?\s*(\d{1,2}:\d{2})',
            'close': r'close\s*(?:time)?\s*:?\s*(\d{1,2}:\d{2})',
            'enroute': r'en\s*route\s*:?\s*(\d{1,2}:\d{2})'
        }
        for field_name, pattern in time_fields.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                fields[f'{field_name}_time'] = match.group(1)

        # Extract event type/terminal
        event_match = re.search(r'(?:event|terminal)\s*:?\s*([A-Z\s]{3,30})', content)
        if event_match:
            fields['event_type'] = event_match.group(1).strip()

        # Extract LOI (Line of Inquiry / Nature of call)
        loi_match = re.search(r'LOI\s*:?\s*([A-Z\s]{3,40})', content, re.IGNORECASE)
        if loi_match:
            fields['nature_of_call'] = loi_match.group(1).strip()

        return fields

    def _calculate_response_time(self, fields: Dict[str, Any]) -> int:
        """
        Calculate response time from dispatch to arrive.

        Args:
            fields: Dict with time fields

        Returns:
            Response time in minutes, or 0 if cannot calculate
        """
        if 'dispatch_time' not in fields or 'arrive_time' not in fields:
            return 0

        try:
            from datetime import datetime
            dispatch = datetime.strptime(fields['dispatch_time'], '%H:%M')
            arrive = datetime.strptime(fields['arrive_time'], '%H:%M')
            diff = arrive - dispatch
            return int(diff.total_seconds() / 60)
        except:
            return 0

    def generate_report(self, conversation: Conversation) -> str:
        """
        Generate human-readable text report of call log analysis.

        Args:
            conversation: Conversation (call log) to analyze

        Returns:
            Formatted text report
        """
        results = self.analyze(conversation)

        if not results['is_call_log']:
            return results['message']

        report = []
        report.append("="*60)
        report.append("CALL LOG ANALYTICS REPORT")
        report.append("="*60)
        report.append("")

        # Overview
        report.append("CALL OVERVIEW")
        report.append("-"*60)
        report.append(f"Total Calls: {results['total_calls']}")
        report.append(f"Completed Calls: {results['completed_calls']}")
        report.append(f"Missed Calls: {results['missed_calls']} ({results['missed_call_percentage']}%)")
        report.append(f"Total Talk Time: {results['total_duration_minutes']} minutes")
        report.append(f"Average Call Duration: {results['average_duration_minutes']} minutes")
        report.append("")

        # Direction
        report.append("CALL DIRECTION")
        report.append("-"*60)
        direction = results['incoming_vs_outgoing']
        report.append(f"Incoming Calls: {direction['incoming']} ({direction['incoming_percentage']}%)")
        report.append(f"Outgoing Calls: {direction['outgoing']} ({direction['outgoing_percentage']}%)")
        report.append("")

        # Top Contacts
        report.append("TOP CONTACTS")
        report.append("-"*60)
        for i, contact in enumerate(results['calls_by_contact'][:5], 1):
            report.append(f"{i}. {contact['contact']}: {contact['call_count']} calls, "
                         f"{contact['total_duration_minutes']}m total, "
                         f"{contact['missed_count']} missed")
        report.append("")

        # Peak Times
        if results['peak_calling_time']:
            peak = results['peak_calling_time']
            report.append("PEAK CALLING TIME")
            report.append("-"*60)
            report.append(f"Busiest Hour: {peak['time_range']} ({peak['call_count']} calls)")

        if results['busiest_day']:
            busy_day = results['busiest_day']
            report.append(f"Busiest Day: {busy_day['day']} ({busy_day['count']} calls)")
        report.append("")

        # Extremes
        if results['longest_call']:
            report.append("CALL DURATION EXTREMES")
            report.append("-"*60)
            longest = results['longest_call']
            report.append(f"Longest Call: {longest['duration_formatted']} with {longest['sender']}")
            if results['shortest_call']:
                shortest = results['shortest_call']
                report.append(f"Shortest Call: {shortest['duration_formatted']} with {shortest['sender']}")

        report.append("")
        report.append("="*60)

        return "\n".join(report)
