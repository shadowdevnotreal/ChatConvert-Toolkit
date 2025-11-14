#!/usr/bin/env python3
"""
CSV to HTML Converter for Chat Logs
Converts chat conversation CSV files into formatted HTML pages.
"""

import csv
import os
from datetime import datetime
from html import escape


def csv_to_html(csv_file_path='chat.csv', output_file='chat_conversation.html'):
    """
    Convert a CSV chat log to an HTML file.

    Args:
        csv_file_path: Path to the input CSV file
        output_file: Path to the output HTML file

    Expected CSV format:
        timestamp, username, message
    """

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found!")
        return False

    try:
        # Read CSV data
        messages = []
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                messages.append(row)

        if not messages:
            print("Warning: No messages found in CSV file!")
            return False

        # Generate HTML
        html_content = generate_html(messages)

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)

        print(f"✓ Successfully converted {len(messages)} messages to HTML!")
        print(f"✓ Output file: {output_file}")
        return True

    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


def generate_html(messages):
    """Generate HTML content from messages."""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Conversation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .chat-container {
            padding: 30px;
            max-height: 700px;
            overflow-y: auto;
        }

        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }

        .username {
            font-weight: bold;
            color: #667eea;
            margin-right: 10px;
            font-size: 15px;
        }

        .timestamp {
            font-size: 12px;
            color: #999;
        }

        .message-content {
            background: #f7f7f7;
            padding: 12px 15px;
            border-radius: 10px;
            border-left: 3px solid #667eea;
            line-height: 1.6;
            color: #333;
        }

        .message:nth-child(even) .message-content {
            background: #e8eaf6;
            border-left-color: #764ba2;
        }

        .message:nth-child(even) .username {
            color: #764ba2;
        }

        .stats {
            background: #f9f9f9;
            padding: 15px 30px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 14px;
        }

        .stats strong {
            color: #667eea;
        }

        /* Scrollbar styling */
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }

        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        .chat-container::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }

        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 Chat Conversation</h1>
            <p>Converted from CSV format</p>
        </div>

        <div class="chat-container">
"""

    # Add messages
    for msg in messages:
        timestamp = escape(msg.get('timestamp', ''))
        username = escape(msg.get('username', 'Unknown'))
        message = escape(msg.get('message', ''))

        html += f"""
            <div class="message">
                <div class="message-header">
                    <span class="username">{username}</span>
                    <span class="timestamp">{timestamp}</span>
                </div>
                <div class="message-content">
                    {message}
                </div>
            </div>
"""

    # Close chat container and add stats
    html += f"""
        </div>

        <div class="stats">
            <strong>{len(messages)}</strong> messages in this conversation
        </div>
    </div>
</body>
</html>
"""

    return html


if __name__ == "__main__":
    print("=" * 50)
    print("CSV to HTML Converter")
    print("=" * 50)

    # Look for CSV files in current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

    if csv_files:
        print(f"\nFound CSV files: {', '.join(csv_files)}")
        csv_file = csv_files[0] if 'chat.csv' not in csv_files else 'chat.csv'
    else:
        csv_file = 'chat.csv'

    print(f"Using: {csv_file}\n")

    csv_to_html(csv_file)
