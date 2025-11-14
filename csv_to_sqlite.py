#!/usr/bin/env python3
"""
CSV to SQLite Converter for Chat Logs
Converts chat conversation CSV files into SQLite database.
"""

import csv
import os
import sqlite3
from datetime import datetime


def csv_to_sqlite(csv_file_path='chat.csv', db_file='chat_conversation.db'):
    """
    Convert a CSV chat log to a SQLite database.

    Args:
        csv_file_path: Path to the input CSV file
        db_file: Path to the output SQLite database file

    Expected CSV format:
        timestamp, username, message
    """

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file '{csv_file_path}' not found!")
        return False

    try:
        # Remove existing database if it exists
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Removed existing database: {db_file}")

        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create messages table
        cursor.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX idx_username ON messages(username)
        ''')

        cursor.execute('''
            CREATE INDEX idx_timestamp ON messages(timestamp)
        ''')

        # Read CSV and insert data
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            message_count = 0

            for row in reader:
                cursor.execute('''
                    INSERT INTO messages (timestamp, username, message)
                    VALUES (?, ?, ?)
                ''', (
                    row.get('timestamp', ''),
                    row.get('username', 'Unknown'),
                    row.get('message', '')
                ))
                message_count += 1

        # Create statistics view
        cursor.execute('''
            CREATE VIEW message_stats AS
            SELECT
                username,
                COUNT(*) as message_count,
                MIN(timestamp) as first_message,
                MAX(timestamp) as last_message
            FROM messages
            GROUP BY username
            ORDER BY message_count DESC
        ''')

        # Commit changes
        conn.commit()

        # Display statistics
        print(f"\n✓ Successfully converted {message_count} messages to SQLite!")
        print(f"✓ Database file: {db_file}")

        print("\n📊 User Statistics:")
        print("-" * 60)
        cursor.execute("SELECT * FROM message_stats")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} messages")

        # Close connection
        conn.close()

        print(f"\n💡 Query examples:")
        print(f"   sqlite3 {db_file} \"SELECT * FROM messages LIMIT 10;\"")
        print(f"   sqlite3 {db_file} \"SELECT * FROM message_stats;\"")

        return True

    except Exception as e:
        print(f"Error during conversion: {e}")
        if 'conn' in locals():
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CSV to SQLite Converter")
    print("=" * 60)

    # Look for CSV files in current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

    if csv_files:
        print(f"\nFound CSV files: {', '.join(csv_files)}")
        csv_file = csv_files[0] if 'chat.csv' not in csv_files else 'chat.csv'
    else:
        csv_file = 'chat.csv'

    print(f"Using: {csv_file}\n")

    csv_to_sqlite(csv_file)
