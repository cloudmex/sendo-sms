import os
import time
import subprocess
from flask import Flask, request, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config
from sms_parser import parse_sms, delete_sms
from api_client import add_internal_credits

app = Flask(__name__)

class SMSHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            # Wait a moment for the file to be fully written
            time.sleep(1)
            self.process_sms(event.src_path)

    def process_sms(self, file_path):
        sms_data = parse_sms(file_path)
        if not sms_data:
            return

        print(f"Processing SMS from {sms_data['sender']}: {sms_data['text']}")

        # Basic parsing logic for "DEPOSIT <CURRENCY> <AMOUNT>"
        parts = sms_data['text'].strip().split()
        if len(parts) == 3 and parts[0].upper() == 'DEPOSIT':
            currency = parts[1].upper()
            try:
                amount = float(parts[2])
                
                # Call API to add credits
                api_response = add_internal_credits(
                    phone_number=sms_data['sender'],
                    currency=currency,
                    amount=amount,
                    note=f"SMS deposit: {sms_data['text']}"
                )

                if api_response and api_response.get('success'):
                    print("API call successful, deleting SMS.")
                    delete_sms(file_path)
                else:
                    print("API call failed, not deleting SMS.")

            except ValueError:
                print(f"Invalid amount in SMS: {parts[2]}")
        else:
            print(f"SMS does not match expected format. Got: {sms_data['text']}")


@app.route('/send-sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    if not data or 'number' not in data or 'message' not in data:
        return jsonify({"success": False, "message": "Missing 'number' or 'message' in request body"}), 400

    number = data['number']
    message = data['message']

    try:
        # Use gammu-smsd-inject to send the SMS
        command = ['gammu-smsd-inject', 'TEXT', number, '-text', message]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        print(f"SMS sent to {number}. Output: {result.stdout}")
        return jsonify({"success": True, "message": "SMS sent successfully", "details": result.stdout})

    except FileNotFoundError:
        error_msg = "Error: 'gammu-smsd-inject' command not found. Is gammu-smsd installed and in your PATH?"
        print(error_msg)
        return jsonify({"success": False, "message": error_msg}), 500
    except subprocess.CalledProcessError as e:
        error_msg = f"Error sending SMS: {e.stderr}"
        print(error_msg)
        return jsonify({"success": False, "message": error_msg, "details": e.stderr}), 500
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg)
        return jsonify({"success": False, "message": error_msg}), 500


def start_observer():
    if not os.path.exists(config.INBOX_PATH):
        print(f"Inbox path {config.INBOX_PATH} does not exist. Creating it.")
        os.makedirs(config.INBOX_PATH)

    event_handler = SMSHandler()
    observer = Observer()
    observer.schedule(event_handler, config.INBOX_PATH, recursive=False)
    observer.start()
    print(f"Watching for new SMS in {config.INBOX_PATH}")
    return observer


if __name__ == "__main__":
    observer = start_observer()
    try:
        app.run(host=config.SERVER_HOST, port=config.SERVER_PORT)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
