"""
Activity Analyzer - Analyzes temporal patterns and user activity.

Provides insights into when messages are sent, who is most active,
and conversation patterns over time.
"""

from typing import Dict, Any, List
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .base_analyzer import BaseAnalyzer
from ..models import Conversation


class ActivityAnalyzer(BaseAnalyzer):
    """Analyze activity patterns and temporal statistics."""

    def analyze(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Analyze activity patterns in conversation.

        Args:
            conversation: Conversation to analyze

        Returns:
            Dict with activity analysis:
            {
                'total_messages': int,
                'date_range': Dict,
                'messages_per_day': List[Dict],
                'messages_per_week': List[Dict],
                'messages_per_month': List[Dict],
                'messages_per_hour': List[Dict],
                'messages_per_weekday': Dict,
                'most_active_participant': Dict,
                'participant_activity': Dict[str, Dict],
                'busiest_day': Dict,
                'busiest_week': Dict,
                'busiest_month': Dict,
                'busiest_hour': int,
                'conversation_duration': Dict,
                'response_times': Dict,
                'frequency_analysis': Dict,
                'conversation_velocity': Dict,
                'burst_periods': List[Dict],
                'dormant_periods': List[Dict]
            }
        """
        self._validate_conversation(conversation)

        # Basic stats
        total_messages = len(conversation.messages)
        date_range = conversation.get_date_range()

        # Timeline analysis
        messages_per_day = self._analyze_daily_activity(conversation)
        messages_per_week = self._analyze_weekly_activity(conversation)
        messages_per_month = self._analyze_monthly_activity(conversation)
        messages_per_hour = self._analyze_hourly_activity(conversation)
        messages_per_weekday = self._analyze_weekday_activity(conversation)

        # Participant analysis
        participant_activity = self._analyze_participant_activity(conversation)

        # Find most active participant
        most_active = max(
            participant_activity.items(),
            key=lambda x: x[1]['message_count']
        ) if participant_activity else (None, {})

        # Find busiest periods
        busiest_day = max(messages_per_day, key=lambda x: x['count']) if messages_per_day else {}
        busiest_week = max(messages_per_week, key=lambda x: x['count']) if messages_per_week else {}
        busiest_month = max(messages_per_month, key=lambda x: x['count']) if messages_per_month else {}

        # Find busiest hour
        busiest_hour_data = max(messages_per_hour, key=lambda x: x['count']) if messages_per_hour else {}
        busiest_hour = busiest_hour_data.get('hour', 0)

        # Conversation duration
        duration = self._calculate_duration(date_range)

        # Response times
        response_times = self._analyze_response_times(conversation)

        # Enhanced frequency analysis
        frequency_analysis = self._analyze_frequency_patterns(conversation)

        # Conversation velocity
        conversation_velocity = self._analyze_conversation_velocity(conversation)

        # Burst and dormant periods
        burst_periods = self._detect_burst_periods(conversation)
        dormant_periods = self._detect_dormant_periods(conversation)

        return {
            'total_messages': total_messages,
            'date_range': {
                'start': date_range[0].isoformat() if date_range[0] else None,
                'end': date_range[1].isoformat() if date_range[1] else None
            },
            'messages_per_day': messages_per_day,
            'messages_per_week': messages_per_week,
            'messages_per_month': messages_per_month,
            'messages_per_hour': messages_per_hour,
            'messages_per_weekday': messages_per_weekday,
            'most_active_participant': {
                'name': most_active[0],
                **most_active[1]
            } if most_active[0] else {},
            'participant_activity': participant_activity,
            'busiest_day': busiest_day,
            'busiest_week': busiest_week,
            'busiest_month': busiest_month,
            'busiest_hour': busiest_hour,
            'conversation_duration': duration,
            'response_times': response_times,
            'frequency_analysis': frequency_analysis,
            'conversation_velocity': conversation_velocity,
            'burst_periods': burst_periods,
            'dormant_periods': dormant_periods
        }

    def _analyze_daily_activity(self, conversation: Conversation) -> List[Dict]:
        """Analyze messages per day."""
        daily_counts = Counter()

        for msg in conversation.messages:
            date = msg.timestamp.date()
            daily_counts[date] += 1

        return [
            {'date': str(date), 'count': count}
            for date, count in sorted(daily_counts.items())
        ]

    def _analyze_hourly_activity(self, conversation: Conversation) -> List[Dict]:
        """Analyze messages per hour of day."""
        hourly_counts = Counter()

        for msg in conversation.messages:
            hour = msg.timestamp.hour
            hourly_counts[hour] += 1

        return [
            {'hour': hour, 'count': hourly_counts.get(hour, 0)}
            for hour in range(24)
        ]

    def _analyze_weekday_activity(self, conversation: Conversation) -> Dict[str, int]:
        """Analyze messages per weekday."""
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_counts = Counter()

        for msg in conversation.messages:
            weekday = msg.timestamp.weekday()
            weekday_counts[weekday_names[weekday]] += 1

        return dict(weekday_counts)

    def _analyze_participant_activity(self, conversation: Conversation) -> Dict[str, Dict]:
        """Analyze activity per participant."""
        participants = conversation.get_participants_list()
        participant_stats = {}

        for participant in participants:
            messages = [msg for msg in conversation.messages if msg.sender == participant]

            if not messages:
                continue

            # Calculate statistics
            message_count = len(messages)
            first_message = min(messages, key=lambda m: m.timestamp)
            last_message = max(messages, key=lambda m: m.timestamp)

            # Average message length
            avg_length = sum(len(msg.content) for msg in messages) / message_count

            # Activity hours
            hours = Counter(msg.timestamp.hour for msg in messages)
            most_active_hour = hours.most_common(1)[0][0] if hours else 0

            participant_stats[participant] = {
                'message_count': message_count,
                'percentage': round(message_count / len(conversation.messages) * 100, 2),
                'average_message_length': round(avg_length, 2),
                'first_message': first_message.timestamp.isoformat(),
                'last_message': last_message.timestamp.isoformat(),
                'most_active_hour': most_active_hour
            }

        return participant_stats

    def _calculate_duration(self, date_range: tuple) -> Dict[str, Any]:
        """Calculate conversation duration."""
        if not date_range[0] or not date_range[1]:
            return {}

        delta = date_range[1] - date_range[0]

        return {
            'days': delta.days,
            'hours': delta.total_seconds() / 3600,
            'human_readable': self._format_duration(delta)
        }

    def _format_duration(self, delta: timedelta) -> str:
        """Format duration in human-readable format."""
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"

    def _analyze_response_times(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze response times between messages."""
        response_times = []
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]

            # Only count if different sender (actual response)
            if prev_msg.sender != curr_msg.sender:
                time_diff = (curr_msg.timestamp - prev_msg.timestamp).total_seconds()
                # Only count reasonable response times (< 24 hours)
                if time_diff < 86400:
                    response_times.append(time_diff)

        if not response_times:
            return {}

        avg_response = sum(response_times) / len(response_times)
        median_response = sorted(response_times)[len(response_times) // 2]

        return {
            'average_seconds': round(avg_response, 2),
            'median_seconds': round(median_response, 2),
            'average_minutes': round(avg_response / 60, 2),
            'median_minutes': round(median_response / 60, 2),
            'sample_size': len(response_times)
        }

    def _analyze_weekly_activity(self, conversation: Conversation) -> List[Dict]:
        """Analyze messages per week."""
        weekly_counts = Counter()

        for msg in conversation.messages:
            # Get ISO week number
            year, week, _ = msg.timestamp.isocalendar()
            week_key = f"{year}-W{week:02d}"
            weekly_counts[week_key] += 1

        return [
            {'week': week, 'count': count}
            for week, count in sorted(weekly_counts.items())
        ]

    def _analyze_monthly_activity(self, conversation: Conversation) -> List[Dict]:
        """Analyze messages per month."""
        monthly_counts = Counter()

        for msg in conversation.messages:
            month_key = msg.timestamp.strftime('%Y-%m')
            monthly_counts[month_key] += 1

        return [
            {'month': month, 'count': count}
            for month, count in sorted(monthly_counts.items())
        ]

    def _analyze_frequency_patterns(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze message frequency patterns."""
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        if len(messages) < 2:
            return {}

        # Calculate inter-message intervals
        intervals = []
        for i in range(1, len(messages)):
            interval = (messages[i].timestamp - messages[i-1].timestamp).total_seconds()
            intervals.append(interval)

        if not intervals:
            return {}

        avg_interval = sum(intervals) / len(intervals)
        median_interval = sorted(intervals)[len(intervals) // 2]

        # Calculate messages per day average
        date_range = conversation.get_date_range()
        if date_range[0] and date_range[1]:
            total_days = (date_range[1] - date_range[0]).days + 1
            messages_per_day_avg = len(messages) / total_days if total_days > 0 else 0
        else:
            messages_per_day_avg = 0

        # Frequency distribution
        frequency_categories = {
            'very_high': 0,  # < 1 min between messages
            'high': 0,       # 1-10 min
            'medium': 0,     # 10-60 min
            'low': 0,        # 1-6 hours
            'very_low': 0    # > 6 hours
        }

        for interval in intervals:
            if interval < 60:
                frequency_categories['very_high'] += 1
            elif interval < 600:
                frequency_categories['high'] += 1
            elif interval < 3600:
                frequency_categories['medium'] += 1
            elif interval < 21600:
                frequency_categories['low'] += 1
            else:
                frequency_categories['very_low'] += 1

        return {
            'average_interval_seconds': round(avg_interval, 2),
            'average_interval_minutes': round(avg_interval / 60, 2),
            'median_interval_seconds': round(median_interval, 2),
            'median_interval_minutes': round(median_interval / 60, 2),
            'messages_per_day_average': round(messages_per_day_avg, 2),
            'frequency_distribution': frequency_categories,
            'sample_size': len(intervals)
        }

    def _analyze_conversation_velocity(self, conversation: Conversation) -> Dict[str, Any]:
        """Analyze conversation velocity (messages per session)."""
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        if len(messages) < 2:
            return {}

        # Define session: messages within 30 minutes of each other
        session_gap_seconds = 1800  # 30 minutes
        sessions = []
        current_session = [messages[0]]

        for i in range(1, len(messages)):
            time_diff = (messages[i].timestamp - messages[i-1].timestamp).total_seconds()

            if time_diff <= session_gap_seconds:
                current_session.append(messages[i])
            else:
                # End current session, start new one
                if current_session:
                    sessions.append(current_session)
                current_session = [messages[i]]

        # Add last session
        if current_session:
            sessions.append(current_session)

        # Calculate velocity metrics
        session_counts = [len(session) for session in sessions]
        avg_messages_per_session = sum(session_counts) / len(sessions) if sessions else 0

        return {
            'total_sessions': len(sessions),
            'average_messages_per_session': round(avg_messages_per_session, 2),
            'longest_session': max(session_counts) if session_counts else 0,
            'shortest_session': min(session_counts) if session_counts else 0,
            'session_gap_threshold_minutes': session_gap_seconds / 60
        }

    def _detect_burst_periods(self, conversation: Conversation) -> List[Dict]:
        """Detect burst periods (high activity in short time)."""
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        if len(messages) < 10:  # Need enough messages to detect bursts
            return []

        # Calculate rolling average of messages per hour
        burst_threshold = 10  # messages per hour
        burst_periods = []

        for i in range(len(messages) - 9):
            # Look at 10-message window
            window_start = messages[i].timestamp
            window_end = messages[i + 9].timestamp
            duration_hours = (window_end - window_start).total_seconds() / 3600

            if duration_hours > 0:
                messages_per_hour = 10 / duration_hours

                if messages_per_hour >= burst_threshold:
                    burst_periods.append({
                        'start': window_start.isoformat(),
                        'end': window_end.isoformat(),
                        'message_count': 10,
                        'messages_per_hour': round(messages_per_hour, 2),
                        'duration_minutes': round(duration_hours * 60, 2)
                    })

        # Merge overlapping burst periods
        merged_bursts = []
        for burst in burst_periods:
            if not merged_bursts or burst['start'] > merged_bursts[-1]['end']:
                merged_bursts.append(burst)
            else:
                # Extend the last burst
                merged_bursts[-1]['end'] = burst['end']

        return merged_bursts[:10]  # Return top 10 burst periods

    def _detect_dormant_periods(self, conversation: Conversation) -> List[Dict]:
        """Detect dormant periods (long gaps in communication)."""
        messages = sorted(conversation.messages, key=lambda m: m.timestamp)

        if len(messages) < 2:
            return []

        dormant_threshold_hours = 24  # Consider > 24 hours as dormant
        dormant_periods = []

        for i in range(1, len(messages)):
            gap_seconds = (messages[i].timestamp - messages[i-1].timestamp).total_seconds()
            gap_hours = gap_seconds / 3600

            if gap_hours >= dormant_threshold_hours:
                dormant_periods.append({
                    'start': messages[i-1].timestamp.isoformat(),
                    'end': messages[i].timestamp.isoformat(),
                    'duration_hours': round(gap_hours, 2),
                    'duration_days': round(gap_hours / 24, 2)
                })

        # Sort by duration and return top 10
        dormant_periods.sort(key=lambda x: x['duration_hours'], reverse=True)
        return dormant_periods[:10]
