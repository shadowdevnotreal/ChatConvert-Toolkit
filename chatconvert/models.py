"""
Core data models for ChatConvert Toolkit.

These models represent the universal data structure that all parsers
convert to and all converters convert from.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class MessageType(Enum):
    """Types of messages."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    STICKER = "sticker"
    LOCATION = "location"
    SYSTEM = "system"
    DELETED = "deleted"


class ReactionType(Enum):
    """Types of reactions."""
    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    CUSTOM = "custom"


@dataclass
class Reaction:
    """A reaction to a message."""
    type: ReactionType
    user: str
    timestamp: Optional[datetime] = None
    emoji: Optional[str] = None  # For custom reactions


@dataclass
class Attachment:
    """File or media attachment."""
    type: MessageType
    filename: str
    url: Optional[str] = None
    local_path: Optional[str] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    base64_data: Optional[str] = None  # Base64-encoded media data (for MMS, embedded images)
    content_id: Optional[str] = None  # Content ID for MMS parts

    def get_data_uri(self) -> Optional[str]:
        """
        Get data URI for embedding in HTML.

        Returns:
            Data URI string like 'data:image/jpeg;base64,/9j/4AAQ...' or None
        """
        if self.base64_data and self.mime_type:
            return f"data:{self.mime_type};base64,{self.base64_data}"
        return None

    def is_image(self) -> bool:
        """Check if attachment is an image."""
        return (self.type == MessageType.IMAGE or
                (self.mime_type and self.mime_type.startswith('image/')))

    def is_video(self) -> bool:
        """Check if attachment is a video."""
        return (self.type == MessageType.VIDEO or
                (self.mime_type and self.mime_type.startswith('video/')))

    def is_audio(self) -> bool:
        """Check if attachment is audio."""
        return (self.type == MessageType.AUDIO or
                (self.mime_type and self.mime_type.startswith('audio/')))


@dataclass
class Message:
    """
    Universal message model.

    All input parsers convert to this format.
    All output converters convert from this format.
    """
    # Required fields
    id: str
    timestamp: datetime
    sender: str
    content: str

    # Optional fields
    type: MessageType = MessageType.TEXT
    reply_to: Optional[str] = None  # Message ID being replied to
    thread_id: Optional[str] = None
    edited: bool = False
    edited_timestamp: Optional[datetime] = None
    deleted: bool = False

    # Rich content
    attachments: List[Attachment] = field(default_factory=list)
    reactions: List[Reaction] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)

    # Platform-specific metadata
    platform: Optional[str] = None
    platform_data: Dict[str, Any] = field(default_factory=dict)

    # Analytics metadata (populated during analysis)
    sentiment_score: Optional[float] = None  # -1 to 1
    sentiment_label: Optional[str] = None  # positive/negative/neutral
    topics: List[str] = field(default_factory=list)
    language: Optional[str] = None


@dataclass
class Participant:
    """A conversation participant."""
    id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None  # admin, moderator, member, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """
    Universal conversation model.

    Container for messages and metadata.
    """
    # Required fields
    id: str
    title: str
    messages: List[Message]

    # Optional fields
    participants: List[Participant] = field(default_factory=list)
    platform: Optional[str] = None
    conversation_type: Optional[str] = None  # dm, group, channel, etc.
    created_at: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Analytics (computed)
    statistics: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        """Return number of messages."""
        return len(self.messages)

    def sort_messages(self):
        """Sort messages by timestamp."""
        self.messages.sort(key=lambda m: m.timestamp)

    def get_date_range(self) -> tuple:
        """Get conversation date range."""
        if not self.messages:
            return None, None
        timestamps = [m.timestamp for m in self.messages]
        return min(timestamps), max(timestamps)

    def get_participants_list(self) -> List[str]:
        """Get unique list of participant usernames."""
        if self.participants:
            return [p.username for p in self.participants]
        return list(set(m.sender for m in self.messages))

    def filter_by_date(self, start: datetime, end: datetime) -> 'Conversation':
        """Return a new Conversation with messages in date range."""
        filtered_messages = [
            m for m in self.messages
            if start <= m.timestamp <= end
        ]
        return Conversation(
            id=self.id,
            title=f"{self.title} (Filtered)",
            messages=filtered_messages,
            participants=self.participants,
            platform=self.platform,
            conversation_type=self.conversation_type,
            created_at=self.created_at,
            metadata=self.metadata
        )

    def filter_by_participants(self, usernames: List[str]) -> 'Conversation':
        """Return a new Conversation with messages from specific participants."""
        filtered_messages = [
            m for m in self.messages
            if m.sender in usernames
        ]
        return Conversation(
            id=self.id,
            title=f"{self.title} (Filtered)",
            messages=filtered_messages,
            participants=[p for p in self.participants if p.username in usernames],
            platform=self.platform,
            conversation_type=self.conversation_type,
            created_at=self.created_at,
            metadata=self.metadata
        )


@dataclass
class ConversionConfig:
    """Configuration for conversion operations."""
    # Input settings
    input_format: Optional[str] = None  # Auto-detect if None
    input_encoding: str = "utf-8"

    # Output settings
    output_format: str = "html"
    output_file: Optional[str] = None

    # Processing options
    include_attachments: bool = True
    include_reactions: bool = True
    include_deleted: bool = False
    include_system_messages: bool = True

    # Filtering
    filter_start_date: Optional[datetime] = None
    filter_end_date: Optional[datetime] = None
    filter_participants: List[str] = field(default_factory=list)
    filter_keywords: List[str] = field(default_factory=list)

    # Analytics
    enable_analytics: bool = False
    enable_sentiment_analysis: bool = False
    enable_topic_modeling: bool = False

    # Privacy
    anonymize_users: bool = False
    redact_pii: bool = False

    # Additional options
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionResult:
    """Result of a conversion operation."""
    success: bool
    output_file: Optional[str] = None
    format: Optional[str] = None
    message_count: int = 0
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
