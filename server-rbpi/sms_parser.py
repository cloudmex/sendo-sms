# server-rbpi/sms_parser.py
import os

def parse_sms(file_path):
    """
    Parses an SMS file as stored by gammu-smsd.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 3:
            return None

        # Example format:
        # Sender: +1234567890
        # Timestamp: 2025-10-29 10:00:00
        #
        # Message body starts here.
        # It can span multiple lines.

        # A more robust way to parse would be to check for specific headers
        # but for now we assume a simple format.
        # A common format is INBOX/IN20251029_100000_00_+1234567890_00.txt
        # Let's assume a simple line-based format first.
        # Based on web search, it can be just lines.

        sender = lines[0].strip()
        timestamp = lines[1].strip()
        text = "".join(lines[2:]).strip()

        return {
            "sender": sender,
            "timestamp": timestamp,
            "text": text
        }
    except Exception as e:
        print(f"Error parsing SMS file {file_path}: {e}")
        return None

def delete_sms(file_path):
    """
    Deletes an SMS file after processing.
    """
    try:
        os.remove(file_path)
        print(f"Deleted processed SMS file: {file_path}")
    except Exception as e:
        print(f"Error deleting SMS file {file_path}: {e}")
