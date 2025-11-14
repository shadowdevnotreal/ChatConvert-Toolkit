"""
Demo Data Generator - Creates realistic sample conversations for demo mode.

Generates:
- Family SMS conversations (group chat)
- Customer service chats (support conversation)
- Call logs (phone calls)
- Technical support (IT troubleshooting with Q&A)
- Emergency dispatch logs (structured data extraction)
- Multi-party group chat (6 participants for network analysis)
- MMS with media (demonstrates media gallery preview)

All data is fake and for demonstration purposes only.
"""

from datetime import datetime, timedelta
import random
from typing import List
import base64

from .models import Conversation, Message, MessageType, Participant, Attachment


class DemoDataGenerator:
    """Generate realistic demo conversation data."""

    @staticmethod
    def generate_family_sms() -> Conversation:
        """
        Generate a realistic family SMS conversation.

        Returns:
            Conversation with family SMS messages
        """
        # Participants
        participants = [
            Participant(id="mom", username="Mom", display_name="Mom 👩"),
            Participant(id="dad", username="Dad", display_name="Dad 👨"),
            Participant(id="alex", username="Alex", display_name="Alex 👦"),
            Participant(id="emma", username="Emma", display_name="Emma 👧")
        ]

        # Base timestamp (3 days ago)
        base_time = datetime.now() - timedelta(days=3)

        # Generate messages
        messages = [
            # Day 1 - Morning
            Message(
                id="1",
                sender="Mom",
                content="Good morning everyone! Don't forget we have dinner at Grandma's tonight at 6pm",
                timestamp=base_time + timedelta(hours=8),
                type=MessageType.TEXT
            ),
            Message(
                id="2",
                sender="Alex",
                content="Morning mom! I'll be there 😊",
                timestamp=base_time + timedelta(hours=8, minutes=5),
                type=MessageType.TEXT
            ),
            Message(
                id="3",
                sender="Emma",
                content="Can I bring my friend Sarah?",
                timestamp=base_time + timedelta(hours=8, minutes=10),
                type=MessageType.TEXT
            ),
            Message(
                id="4",
                sender="Mom",
                content="Of course honey! The more the merrier 🎉",
                timestamp=base_time + timedelta(hours=8, minutes=12),
                type=MessageType.TEXT
            ),
            Message(
                id="5",
                sender="Dad",
                content="Should I pick up dessert on my way home from work?",
                timestamp=base_time + timedelta(hours=9),
                type=MessageType.TEXT
            ),
            Message(
                id="6",
                sender="Mom",
                content="That would be great! Grandma loves that chocolate cake from the bakery on Main Street",
                timestamp=base_time + timedelta(hours=9, minutes=3),
                type=MessageType.TEXT
            ),
            Message(
                id="7",
                sender="Dad",
                content="Will do! 🍰",
                timestamp=base_time + timedelta(hours=9, minutes=5),
                type=MessageType.TEXT
            ),

            # Day 1 - Afternoon
            Message(
                id="8",
                sender="Alex",
                content="Mom, I'm running late with soccer practice. Will probably be there around 6:15",
                timestamp=base_time + timedelta(hours=16),
                type=MessageType.TEXT
            ),
            Message(
                id="9",
                sender="Mom",
                content="No problem sweetie, we'll wait for you!",
                timestamp=base_time + timedelta(hours=16, minutes=2),
                type=MessageType.TEXT
            ),

            # Day 1 - Evening
            Message(
                id="10",
                sender="Emma",
                content="Thanks for dinner everyone! Grandma's lasagna was amazing as always ❤️",
                timestamp=base_time + timedelta(hours=20),
                type=MessageType.TEXT
            ),
            Message(
                id="11",
                sender="Alex",
                content="Agreed! Love you all",
                timestamp=base_time + timedelta(hours=20, minutes=2),
                type=MessageType.TEXT
            ),

            # Day 2 - Weekend plans
            Message(
                id="12",
                sender="Dad",
                content="Who wants to go hiking tomorrow? Weather looks perfect!",
                timestamp=base_time + timedelta(days=1, hours=19),
                type=MessageType.TEXT
            ),
            Message(
                id="13",
                sender="Emma",
                content="Count me in! 🥾",
                timestamp=base_time + timedelta(days=1, hours=19, minutes=5),
                type=MessageType.TEXT
            ),
            Message(
                id="14",
                sender="Alex",
                content="I have a study group in the morning, but I can join after lunch?",
                timestamp=base_time + timedelta(days=1, hours=19, minutes=8),
                type=MessageType.TEXT
            ),
            Message(
                id="15",
                sender="Mom",
                content="That works! We can start around 2pm. I'll pack sandwiches 🥪",
                timestamp=base_time + timedelta(days=1, hours=19, minutes=10),
                type=MessageType.TEXT
            ),
            Message(
                id="16",
                sender="Dad",
                content="Perfect! Meet at the trailhead parking lot at 2pm",
                timestamp=base_time + timedelta(days=1, hours=19, minutes=15),
                type=MessageType.TEXT
            ),

            # Day 3 - After hike
            Message(
                id="17",
                sender="Alex",
                content="That was an awesome hike! My legs are so sore though 😅",
                timestamp=base_time + timedelta(days=2, hours=17),
                type=MessageType.TEXT
            ),
            Message(
                id="18",
                sender="Emma",
                content="Same! But the view from the top was totally worth it 🏔️",
                timestamp=base_time + timedelta(days=2, hours=17, minutes=3),
                type=MessageType.TEXT
            ),
            Message(
                id="19",
                sender="Mom",
                content="Great job everyone! Love our family adventures ❤️",
                timestamp=base_time + timedelta(days=2, hours=17, minutes=5),
                type=MessageType.TEXT
            ),
            Message(
                id="20",
                sender="Dad",
                content="Best family ever! Same time next month? 😊",
                timestamp=base_time + timedelta(days=2, hours=17, minutes=8),
                type=MessageType.TEXT
            ),
        ]

        return Conversation(
            id="demo_family_sms",
            title="Family Group Chat",
            messages=messages,
            participants=participants,
            platform="SMS",
            conversation_type="group",
            created_at=base_time
        )

    @staticmethod
    def generate_customer_service_chat() -> Conversation:
        """
        Generate a realistic customer service chat conversation.

        Returns:
            Conversation with customer service messages
        """
        # Participants
        participants = [
            Participant(id="customer", username="Jordan", display_name="Jordan Smith"),
            Participant(id="agent", username="SupportAgent", display_name="Sarah (Support Agent)")
        ]

        # Base timestamp (2 hours ago)
        base_time = datetime.now() - timedelta(hours=2)

        # Generate messages
        messages = [
            Message(
                id="1",
                sender="Jordan",
                content="Hi, I need help with my recent order #ORD-12345",
                timestamp=base_time,
                type=MessageType.TEXT
            ),
            Message(
                id="2",
                sender="SupportAgent",
                content="Hello Jordan! I'd be happy to help you with your order. Could you please tell me what issue you're experiencing?",
                timestamp=base_time + timedelta(minutes=1),
                type=MessageType.TEXT
            ),
            Message(
                id="3",
                sender="Jordan",
                content="The package was supposed to arrive yesterday but it still hasn't shown up. The tracking says it's 'out for delivery' since 2 days ago",
                timestamp=base_time + timedelta(minutes=2),
                type=MessageType.TEXT
            ),
            Message(
                id="4",
                sender="SupportAgent",
                content="I understand how frustrating that must be. Let me look into this for you right away.",
                timestamp=base_time + timedelta(minutes=3),
                type=MessageType.TEXT
            ),
            Message(
                id="5",
                sender="SupportAgent",
                content="I'm pulling up your order details now... one moment please.",
                timestamp=base_time + timedelta(minutes=3, seconds=30),
                type=MessageType.TEXT
            ),
            Message(
                id="6",
                sender="Jordan",
                content="Thank you! I appreciate your help",
                timestamp=base_time + timedelta(minutes=4),
                type=MessageType.TEXT
            ),
            Message(
                id="7",
                sender="SupportAgent",
                content="I can see that there was a delivery exception due to an incorrect address. The package is currently at our local distribution center. I can arrange for immediate redelivery to your correct address. Could you please confirm your delivery address?",
                timestamp=base_time + timedelta(minutes=5),
                type=MessageType.TEXT
            ),
            Message(
                id="8",
                sender="Jordan",
                content="Oh no! The address should be 123 Maple Street, Apt 4B, Springfield, IL 62701",
                timestamp=base_time + timedelta(minutes=6),
                type=MessageType.TEXT
            ),
            Message(
                id="9",
                sender="SupportAgent",
                content="Perfect! I've updated your address and expedited the delivery. Your package will be delivered tomorrow by end of day. You should receive a new tracking number via email within the next hour.",
                timestamp=base_time + timedelta(minutes=7),
                type=MessageType.TEXT
            ),
            Message(
                id="10",
                sender="Jordan",
                content="That's great news! Will there be any additional charges for the redelivery?",
                timestamp=base_time + timedelta(minutes=8),
                type=MessageType.TEXT
            ),
            Message(
                id="11",
                sender="SupportAgent",
                content="Not at all! Since this was our error, the expedited redelivery is completely free. As an apology for the inconvenience, I've also applied a 15% discount code to your account for your next purchase.",
                timestamp=base_time + timedelta(minutes=9),
                type=MessageType.TEXT
            ),
            Message(
                id="12",
                sender="Jordan",
                content="Wow, thank you so much! That's really appreciated. You've been so helpful 😊",
                timestamp=base_time + timedelta(minutes=10),
                type=MessageType.TEXT
            ),
            Message(
                id="13",
                sender="SupportAgent",
                content="You're very welcome! Is there anything else I can help you with today?",
                timestamp=base_time + timedelta(minutes=11),
                type=MessageType.TEXT
            ),
            Message(
                id="14",
                sender="Jordan",
                content="No, that's everything. Thanks again!",
                timestamp=base_time + timedelta(minutes=12),
                type=MessageType.TEXT
            ),
            Message(
                id="15",
                sender="SupportAgent",
                content="My pleasure! Have a wonderful day, and don't hesitate to reach out if you need anything else. Take care! 👋",
                timestamp=base_time + timedelta(minutes=13),
                type=MessageType.TEXT
            ),
        ]

        return Conversation(
            id="demo_customer_service",
            title="Customer Support Chat - Order #ORD-12345",
            messages=messages,
            participants=participants,
            platform="Live Chat",
            conversation_type="dm",
            created_at=base_time
        )

    @staticmethod
    def generate_call_log() -> Conversation:
        """
        Generate a realistic call log.

        Returns:
            Conversation with call log entries
        """
        # Participants (contacts)
        participants = [
            Participant(id="me", username="Me", display_name="Me"),
            Participant(id="mom", username="Mom", display_name="Mom"),
            Participant(id="work", username="Office", display_name="Office"),
            Participant(id="friend", username="Mike", display_name="Mike"),
            Participant(id="unknown", username="Unknown", display_name="(Unknown)")
        ]

        # Base timestamp (7 days ago)
        base_time = datetime.now() - timedelta(days=7)

        # Generate call log messages
        messages = [
            # Day 1
            Message(
                id="1",
                sender="Mom",
                content="📞 Call duration: 8m 32s\nContact: Mom\nNumber: +1-555-0123\nTime: 2025-11-01 09:15:00",
                timestamp=base_time + timedelta(hours=9, minutes=15),
                type=MessageType.TEXT
            ),
            Message(
                id="2",
                sender="Office",
                content="📞 Call duration: 15m 47s\nContact: Office\nNumber: +1-555-0199\nTime: 2025-11-01 10:30:00",
                timestamp=base_time + timedelta(hours=10, minutes=30),
                type=MessageType.TEXT
            ),
            Message(
                id="3",
                sender="Unknown",
                content="❌ Missed call\nNumber: +1-555-0987\nTime: 2025-11-01 14:22:00",
                timestamp=base_time + timedelta(hours=14, minutes=22),
                type=MessageType.TEXT
            ),

            # Day 2
            Message(
                id="4",
                sender="Mike",
                content="📞 Call duration: 23m 15s\nContact: Mike\nNumber: +1-555-0456\nTime: 2025-11-02 19:00:00",
                timestamp=base_time + timedelta(days=1, hours=19),
                type=MessageType.TEXT
            ),
            Message(
                id="5",
                sender="Mom",
                content="📞 Call duration: 5m 12s\nContact: Mom\nNumber: +1-555-0123\nTime: 2025-11-02 20:30:00",
                timestamp=base_time + timedelta(days=1, hours=20, minutes=30),
                type=MessageType.TEXT
            ),

            # Day 3
            Message(
                id="6",
                sender="Office",
                content="📞 Call duration: 32m 8s\nContact: Office\nNumber: +1-555-0199\nTime: 2025-11-03 09:00:00",
                timestamp=base_time + timedelta(days=2, hours=9),
                type=MessageType.TEXT
            ),
            Message(
                id="7",
                sender="Unknown",
                content="❌ Missed call\nNumber: +1-555-0111\nTime: 2025-11-03 11:45:00",
                timestamp=base_time + timedelta(days=2, hours=11, minutes=45),
                type=MessageType.TEXT
            ),
            Message(
                id="8",
                sender="Mike",
                content="📞 Call duration: 2m 34s\nContact: Mike\nNumber: +1-555-0456\nTime: 2025-11-03 16:20:00",
                timestamp=base_time + timedelta(days=2, hours=16, minutes=20),
                type=MessageType.TEXT
            ),

            # Day 4
            Message(
                id="9",
                sender="Mom",
                content="📞 Call duration: 12m 3s\nContact: Mom\nNumber: +1-555-0123\nTime: 2025-11-04 18:00:00",
                timestamp=base_time + timedelta(days=3, hours=18),
                type=MessageType.TEXT
            ),
            Message(
                id="10",
                sender="Office",
                content="❌ Missed call\nContact: Office\nNumber: +1-555-0199\nTime: 2025-11-04 20:15:00",
                timestamp=base_time + timedelta(days=3, hours=20, minutes=15),
                type=MessageType.TEXT
            ),

            # Day 5
            Message(
                id="11",
                sender="Mike",
                content="📞 Call duration: 45m 22s\nContact: Mike\nNumber: +1-555-0456\nTime: 2025-11-05 19:30:00",
                timestamp=base_time + timedelta(days=4, hours=19, minutes=30),
                type=MessageType.TEXT
            ),

            # Day 6
            Message(
                id="12",
                sender="Mom",
                content="📞 Call duration: 7m 45s\nContact: Mom\nNumber: +1-555-0123\nTime: 2025-11-06 10:00:00",
                timestamp=base_time + timedelta(days=5, hours=10),
                type=MessageType.TEXT
            ),
            Message(
                id="13",
                sender="Unknown",
                content="❌ Missed call\nNumber: +1-555-0777\nTime: 2025-11-06 13:30:00",
                timestamp=base_time + timedelta(days=5, hours=13, minutes=30),
                type=MessageType.TEXT
            ),
            Message(
                id="14",
                sender="Office",
                content="📞 Call duration: 18m 55s\nContact: Office\nNumber: +1-555-0199\nTime: 2025-11-06 15:00:00",
                timestamp=base_time + timedelta(days=5, hours=15),
                type=MessageType.TEXT
            ),

            # Day 7
            Message(
                id="15",
                sender="Mom",
                content="📞 Call duration: 3m 18s\nContact: Mom\nNumber: +1-555-0123\nTime: 2025-11-07 09:30:00",
                timestamp=base_time + timedelta(days=6, hours=9, minutes=30),
                type=MessageType.TEXT
            ),
        ]

        return Conversation(
            id="demo_call_log",
            title="Call Log - Last 7 Days",
            messages=messages,
            participants=participants,
            platform="Phone",
            conversation_type="call_log",
            created_at=base_time
        )

    @staticmethod
    def generate_tech_support() -> Conversation:
        """
        Generate a realistic technical support conversation with troubleshooting.

        Returns:
            Conversation with IT support messages
        """
        participants = [
            Participant(id="user", username="JohnD", display_name="John (User)"),
            Participant(id="tech", username="TechSupport", display_name="Alex (IT Support)")
        ]

        base_time = datetime.now() - timedelta(hours=1)

        messages = [
            Message(
                id="1",
                sender="JohnD",
                content="Hi, I'm having trouble connecting to the VPN. It keeps saying 'Connection timeout'",
                timestamp=base_time,
                type=MessageType.TEXT
            ),
            Message(
                id="2",
                sender="TechSupport",
                content="Hello John! I can help you with that. Let's troubleshoot this step by step. First, can you tell me which VPN client you're using?",
                timestamp=base_time + timedelta(minutes=1),
                type=MessageType.TEXT
            ),
            Message(
                id="3",
                sender="JohnD",
                content="I'm using Cisco AnyConnect version 4.10",
                timestamp=base_time + timedelta(minutes=2),
                type=MessageType.TEXT
            ),
            Message(
                id="4",
                sender="TechSupport",
                content="Perfect. Can you try these steps:\n1. Disconnect from VPN\n2. Clear the VPN cache: Go to Settings > Reset Statistics\n3. Restart the VPN client\n4. Try connecting again",
                timestamp=base_time + timedelta(minutes=3),
                type=MessageType.TEXT
            ),
            Message(
                id="5",
                sender="JohnD",
                content="Okay, trying that now...",
                timestamp=base_time + timedelta(minutes=4),
                type=MessageType.TEXT
            ),
            Message(
                id="6",
                sender="JohnD",
                content="Still getting the same error. The connection times out after about 30 seconds",
                timestamp=base_time + timedelta(minutes=6),
                type=MessageType.TEXT
            ),
            Message(
                id="7",
                sender="TechSupport",
                content="Alright, let's check your network settings. Are you on WiFi or Ethernet?",
                timestamp=base_time + timedelta(minutes=7),
                type=MessageType.TEXT
            ),
            Message(
                id="8",
                sender="JohnD",
                content="WiFi. Should I switch to Ethernet?",
                timestamp=base_time + timedelta(minutes=8),
                type=MessageType.TEXT
            ),
            Message(
                id="9",
                sender="TechSupport",
                content="Yes, please try Ethernet if possible. Also, can you ping the VPN gateway? Open Command Prompt and type: ping vpn.company.com",
                timestamp=base_time + timedelta(minutes=9),
                type=MessageType.TEXT
            ),
            Message(
                id="10",
                sender="JohnD",
                content="Ping results:\nPinging vpn.company.com [192.168.100.1]\nReply from 192.168.100.1: bytes=32 time=45ms TTL=64\nReply from 192.168.100.1: bytes=32 time=42ms TTL=64",
                timestamp=base_time + timedelta(minutes=11),
                type=MessageType.TEXT
            ),
            Message(
                id="11",
                sender="TechSupport",
                content="Great! The gateway is reachable. The issue might be with your firewall. Can you temporarily disable Windows Firewall and try connecting?",
                timestamp=base_time + timedelta(minutes=12),
                type=MessageType.TEXT
            ),
            Message(
                id="12",
                sender="JohnD",
                content="OMG it worked! Connected successfully. So it's a firewall issue?",
                timestamp=base_time + timedelta(minutes=14),
                type=MessageType.TEXT
            ),
            Message(
                id="13",
                sender="TechSupport",
                content="Exactly! Your firewall is blocking the VPN ports. I'll add an exception rule for the VPN client. Can you keep the firewall off for now? I'll send you a configuration file via email in 10 minutes that will fix this permanently.",
                timestamp=base_time + timedelta(minutes=15),
                type=MessageType.TEXT
            ),
            Message(
                id="14",
                sender="JohnD",
                content="Perfect! Thank you so much for your help. That was driving me crazy!",
                timestamp=base_time + timedelta(minutes=16),
                type=MessageType.TEXT
            ),
            Message(
                id="15",
                sender="TechSupport",
                content="You're welcome! I've created ticket #IT-5678 for this issue. You'll receive the firewall configuration within 10 minutes. Let me know if you have any other issues!",
                timestamp=base_time + timedelta(minutes=17),
                type=MessageType.TEXT
            ),
        ]

        return Conversation(
            id="demo_tech_support",
            title="IT Support - VPN Troubleshooting",
            messages=messages,
            participants=participants,
            platform="Help Desk",
            conversation_type="dm",
            created_at=base_time
        )

    @staticmethod
    def generate_dispatch_log() -> Conversation:
        """
        Generate a realistic emergency dispatch log with structured data.

        Returns:
            Conversation with dispatch call entries
        """
        participants = [
            Participant(id="dispatch", username="Dispatch", display_name="Dispatch Center")
        ]

        base_time = datetime.now() - timedelta(hours=4)

        messages = [
            Message(
                id="1",
                sender="Dispatch",
                content="""Emergency Dispatch Report
Case Number: 2025-001234
Event: Medical Emergency - Chest Pain
Location: 450 Oak Street, Apartment 3B, Downtown Sector
Caller Phone: 555-0198
Call Source: 911
Priority: HIGH
Dispatch: 14:23
Enroute: 14:25
Arrive: 14:31
Close: 15:02
Response Time: 8 minutes
Remarks: Patient transported to Memorial Hospital. Stable condition.""",
                timestamp=base_time,
                type=MessageType.TEXT
            ),
            Message(
                id="2",
                sender="Dispatch",
                content="""Emergency Dispatch Report
Case Number: 2025-001235
Event: Structure Fire - Residential
Location: 789 Elm Avenue, Westside Sector
Caller Phone: 555-0145
Call Source: Neighbor Report
Priority: CRITICAL
Dispatch: 14:45
Enroute: 14:47
Arrive: 14:54
Close: 16:20
Response Time: 9 minutes
Remarks: Fire contained to kitchen. No injuries. Building safe for occupancy.""",
                timestamp=base_time + timedelta(minutes=22),
                type=MessageType.TEXT
            ),
            Message(
                id="3",
                sender="Dispatch",
                content="""Emergency Dispatch Report
Case Number: 2025-001236
Event: Traffic Accident - Vehicle Collision
Location: Highway 101 Northbound, Mile Marker 23
Caller Phone: 555-0167
Call Source: Highway Patrol
Priority: MEDIUM
Dispatch: 15:10
Enroute: 15:12
Arrive: 15:18
Close: 15:45
Response Time: 6 minutes
Remarks: Minor injuries. Two vehicles towed. Traffic cleared.""",
                timestamp=base_time + timedelta(minutes=47),
                type=MessageType.TEXT
            ),
            Message(
                id="4",
                sender="Dispatch",
                content="""Emergency Dispatch Report
Case Number: 2025-001237
Event: Burglary in Progress
Location: 234 Maple Drive, Eastside Sector
Caller Phone: 555-0189
Call Source: Homeowner
Priority: HIGH
Dispatch: 15:55
Enroute: 15:56
Arrive: 16:03
Close: 16:45
Response Time: 7 minutes
Remarks: Suspect apprehended. Property recovered. Arrest made.""",
                timestamp=base_time + timedelta(minutes=92),
                type=MessageType.TEXT
            ),
            Message(
                id="5",
                sender="Dispatch",
                content="""Emergency Dispatch Report
Case Number: 2025-001238
Event: Gas Leak - Hazardous Materials
Location: 567 Pine Street, Commercial District
Caller Phone: 555-0123
Call Source: Business Owner
Priority: CRITICAL
Dispatch: 16:30
Enroute: 16:32
Arrive: 16:39
Close: 17:55
Response Time: 7 minutes
Remarks: Gas company notified. Building evacuated. Leak repaired. All clear.""",
                timestamp=base_time + timedelta(minutes=127),
                type=MessageType.TEXT
            ),
        ]

        return Conversation(
            id="demo_dispatch",
            title="Emergency Dispatch Log - 4 Hour Period",
            messages=messages,
            participants=participants,
            platform="Dispatch System",
            conversation_type="call_log",
            created_at=base_time
        )

    @staticmethod
    def generate_group_chat() -> Conversation:
        """
        Generate a large group chat for network analysis demo.

        Returns:
            Conversation with 6 participants and complex interaction patterns
        """
        participants = [
            Participant(id="alice", username="Alice", display_name="Alice 👩"),
            Participant(id="bob", username="Bob", display_name="Bob 👨"),
            Participant(id="carol", username="Carol", display_name="Carol 👩"),
            Participant(id="dave", username="Dave", display_name="Dave 👨"),
            Participant(id="eve", username="Eve", display_name="Eve 👩"),
            Participant(id="frank", username="Frank", display_name="Frank 👨")
        ]

        base_time = datetime.now() - timedelta(days=1)

        messages = [
            # Planning meeting
            Message(id="1", sender="Alice", content="Hey everyone! Let's plan the team offsite for next month. Any location ideas?",
                   timestamp=base_time, type=MessageType.TEXT),
            Message(id="2", sender="Bob", content="How about the mountains? There's a great retreat center near Lake Tahoe",
                   timestamp=base_time + timedelta(minutes=2), type=MessageType.TEXT),
            Message(id="3", sender="Carol", content="I second that! Mountains would be perfect. Good hiking trails too",
                   timestamp=base_time + timedelta(minutes=4), type=MessageType.TEXT),
            Message(id="4", sender="Dave", content="What about the beach instead? We could do some team building on the coast",
                   timestamp=base_time + timedelta(minutes=6), type=MessageType.TEXT),
            Message(id="5", sender="Eve", content="Beach sounds amazing! @Dave do you have a specific location in mind?",
                   timestamp=base_time + timedelta(minutes=8), type=MessageType.TEXT),
            Message(id="6", sender="Dave", content="@Eve I was thinking Santa Cruz. Lots of activities there",
                   timestamp=base_time + timedelta(minutes=10), type=MessageType.TEXT),
            Message(id="7", sender="Frank", content="Both options sound great. Maybe we should vote?",
                   timestamp=base_time + timedelta(minutes=12), type=MessageType.TEXT),
            Message(id="8", sender="Alice", content="Good idea @Frank. Let's do a quick poll: Mountains vs Beach",
                   timestamp=base_time + timedelta(minutes=14), type=MessageType.TEXT),

            # Later discussion
            Message(id="9", sender="Bob", content="By the way, has anyone reviewed the Q4 budget proposal?",
                   timestamp=base_time + timedelta(hours=2), type=MessageType.TEXT),
            Message(id="10", sender="Carol", content="@Bob I looked at it yesterday. Seems reasonable overall",
                   timestamp=base_time + timedelta(hours=2, minutes=5), type=MessageType.TEXT),
            Message(id="11", sender="Eve", content="@Bob @Carol I have some concerns about the marketing allocation",
                   timestamp=base_time + timedelta(hours=2, minutes=10), type=MessageType.TEXT),
            Message(id="12", sender="Alice", content="@Eve Let's discuss that in tomorrow's meeting. Good catch!",
                   timestamp=base_time + timedelta(hours=2, minutes=15), type=MessageType.TEXT),

            # Evening chat
            Message(id="13", sender="Dave", content="Anyone want to grab lunch tomorrow?",
                   timestamp=base_time + timedelta(hours=7), type=MessageType.TEXT),
            Message(id="14", sender="Frank", content="I'm in! @Carol @Eve you coming?",
                   timestamp=base_time + timedelta(hours=7, minutes=3), type=MessageType.TEXT),
            Message(id="15", sender="Carol", content="Count me in! Where should we go?",
                   timestamp=base_time + timedelta(hours=7, minutes=5), type=MessageType.TEXT),
            Message(id="16", sender="Eve", content="I can't tomorrow, but have fun everyone!",
                   timestamp=base_time + timedelta(hours=7, minutes=7), type=MessageType.TEXT),
            Message(id="17", sender="Bob", content="@Dave I'll join too. How about that new Italian place?",
                   timestamp=base_time + timedelta(hours=7, minutes=10), type=MessageType.TEXT),
            Message(id="18", sender="Dave", content="Perfect! @Bob @Frank @Carol - 12:30pm at Luigi's?",
                   timestamp=base_time + timedelta(hours=7, minutes=12), type=MessageType.TEXT),
            Message(id="19", sender="Frank", content="See you there! 👍",
                   timestamp=base_time + timedelta(hours=7, minutes=15), type=MessageType.TEXT),
            Message(id="20", sender="Alice", content="Sounds fun! Wish I could join but I have a client meeting",
                   timestamp=base_time + timedelta(hours=7, minutes=18), type=MessageType.TEXT),

            # Next day
            Message(id="21", sender="Carol", content="Great lunch yesterday everyone! Thanks @Dave for organizing",
                   timestamp=base_time + timedelta(days=1, hours=14), type=MessageType.TEXT),
            Message(id="22", sender="Bob", content="Yeah that was awesome! We should do it more often",
                   timestamp=base_time + timedelta(days=1, hours=14, minutes=5), type=MessageType.TEXT),
            Message(id="23", sender="Frank", content="Agreed! Next time we'll drag @Eve and @Alice along too 😄",
                   timestamp=base_time + timedelta(days=1, hours=14, minutes=10), type=MessageType.TEXT),
        ]

        return Conversation(
            id="demo_group_chat",
            title="Work Team Group Chat",
            messages=messages,
            participants=participants,
            platform="Slack",
            conversation_type="group",
            created_at=base_time
        )

    @staticmethod
    def generate_mms_media() -> Conversation:
        """
        Generate an MMS conversation with media attachments (demo with small image data).

        Returns:
            Conversation with MMS messages containing media
        """
        participants = [
            Participant(id="me", username="Me", display_name="Me"),
            Participant(id="sarah", username="Sarah", display_name="Sarah")
        ]

        base_time = datetime.now() - timedelta(hours=3)

        # Create a tiny 1x1 red pixel PNG for demo (valid base64 image data)
        tiny_red_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

        # Create a tiny 1x1 blue pixel PNG
        tiny_blue_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M/wHwAEBgIApD5fRAAAAABJRU5ErkJggg=="

        messages = [
            Message(
                id="1",
                sender="Sarah",
                content="Hey! Check out this photo from the beach yesterday 🏖️",
                timestamp=base_time,
                type=MessageType.IMAGE,
                attachments=[
                    Attachment(
                        type=MessageType.IMAGE,
                        filename="beach_sunset.jpg",
                        mime_type="image/png",
                        base64_data=tiny_red_pixel,
                        size_bytes=150
                    )
                ]
            ),
            Message(
                id="2",
                sender="Me",
                content="Wow, that's beautiful! The sunset colors are amazing",
                timestamp=base_time + timedelta(minutes=2),
                type=MessageType.TEXT
            ),
            Message(
                id="3",
                sender="Sarah",
                content="I know right? Here's another one from earlier",
                timestamp=base_time + timedelta(minutes=5),
                type=MessageType.IMAGE,
                attachments=[
                    Attachment(
                        type=MessageType.IMAGE,
                        filename="beach_waves.jpg",
                        mime_type="image/png",
                        base64_data=tiny_blue_pixel,
                        size_bytes=145
                    )
                ]
            ),
            Message(
                id="4",
                sender="Me",
                content="The water looks so clear! When can we go together?",
                timestamp=base_time + timedelta(minutes=7),
                type=MessageType.TEXT
            ),
            Message(
                id="5",
                sender="Sarah",
                content="How about next weekend? Weather should be perfect!",
                timestamp=base_time + timedelta(minutes=10),
                type=MessageType.TEXT
            ),
            Message(
                id="6",
                sender="Me",
                content="Perfect! I'll bring my camera too 📸",
                timestamp=base_time + timedelta(minutes=12),
                type=MessageType.TEXT
            ),
            Message(
                id="7",
                sender="Sarah",
                content="Great! Can't wait 😊",
                timestamp=base_time + timedelta(minutes=15),
                type=MessageType.TEXT
            ),
        ]

        return Conversation(
            id="demo_mms_media",
            title="MMS Conversation with Photos",
            messages=messages,
            participants=participants,
            platform="MMS",
            conversation_type="dm",
            created_at=base_time
        )

    @classmethod
    def get_demo_conversation(cls, demo_type: str) -> Conversation:
        """
        Get a demo conversation by type.

        Args:
            demo_type: Type of demo ('family', 'customer_service', 'call_log')

        Returns:
            Demo conversation

        Raises:
            ValueError: If demo_type is invalid
        """
        demo_map = {
            'family': cls.generate_family_sms,
            'customer_service': cls.generate_customer_service_chat,
            'call_log': cls.generate_call_log,
            'tech_support': cls.generate_tech_support,
            'dispatch': cls.generate_dispatch_log,
            'group_chat': cls.generate_group_chat,
            'mms_media': cls.generate_mms_media
        }

        if demo_type not in demo_map:
            raise ValueError(f"Invalid demo type: {demo_type}. Choose from: {list(demo_map.keys())}")

        return demo_map[demo_type]()

    @classmethod
    def list_demo_types(cls) -> List[str]:
        """Get list of available demo types."""
        return ['family', 'customer_service', 'call_log', 'tech_support', 'dispatch', 'group_chat', 'mms_media']
