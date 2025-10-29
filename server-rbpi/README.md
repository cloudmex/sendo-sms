# SMS Gateway for Raspberry Pi

This Python server is designed to run on a Raspberry Pi with a connected GSM modem. It uses `gammu-smsd` to handle SMS sending and receiving.

## Features

-   **Incoming SMS Processing**: Monitors a directory for new SMS files created by `gammu-smsd`, parses them, and calls an external API.
-   **API Integration**: Calls the `api-sendo` to perform operations based on SMS content (e.g., adding credits for a user).
-   **Send SMS Endpoint**: Provides an HTTP endpoint (`/send-sms`) to send SMS messages.
-   **Robust**: Less coupling with `gammu-smsd` by using the filesystem as an interface.

## How It Works

1.  **`gammu-smsd`**: This daemon is responsible for interfacing with the GSM modem.
    -   **Incoming SMS**: `gammu-smsd` is configured to store incoming SMS messages as files in an `inbox` directory.
    -   **Outgoing SMS**: The server uses `gammu-smsd-inject` to queue outgoing SMS messages.

2.  **Python Server (`app.py`)**:
    -   A `watchdog` observer monitors the `inbox` directory for new files.
    -   When a new SMS file is detected, it's parsed by `sms_parser.py`.
    -   The server expects SMS in the format `DEPOSIT <CURRENCY> <AMOUNT>`.
    -   If the format is correct, `api_client.py` makes a POST request to the `api-sendo`'s `/monitor/internal-credits` endpoint.
    -   If the API call is successful, the processed SMS file is deleted.
    -   A Flask web server provides the `/send-sms` endpoint.

## Setup

### Prerequisites

-   Raspberry Pi with Raspberry Pi OS.
-   A GSM modem compatible with Gammu.
-   Python 3.
-   `gammu` and `gammu-smsd` installed.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd sendo-sms/server-rbpi
    ```

2.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure `gammu-smsd`**:
    Edit the `gammu-smsdrc` file (usually at `/etc/gammu-smsdrc`).
    -   Configure your modem under `[gammu]`.
    -   Set up the file service under `[smsd]`. **Important**: Do not use `RunOnReceive`. The Python server handles processing from the inbox.

    ```ini
    [gammu]
    port = /dev/ttyUSB0  # Change to your modem's port
    connection = at

    [smsd]
    service = files
    inboxpath = /var/spool/gammu/inbox/
    outboxpath = /var/spool/gammu/outbox/
    sentsmspath = /var/spool/gammu/sent/
    errorsmspath = /var/spool/gammu/error/
    ```

4.  **Start `gammu-smsd` service**:
    ```bash
    sudo systemctl start gammu-smsd
    ```
    Check its status to ensure it's running correctly:
    ```bash
    sudo systemctl status gammu-smsd
    ```

5.  **Configure the Python server**:
    Edit `server-rbpi/config.py`:
    -   `INBOX_PATH`: Should match `inboxpath` from your `gammu-smsdrc`.
    -   `API_SENDO_URL`: Set the correct URL for your `api-sendo` instance.

### Running the Server

To run the server:
```bash
python app.py
```
The server will start, and you will see a message that it's watching the inbox directory.

## Usage

### Receiving and Processing SMS

-   When an SMS is received by the modem, `gammu-smsd` will save it as a file in the configured `inbox` directory.
-   The Python server will detect the new file, parse it, and call the API.
-   Check the server's console output for logs of this process.

### Sending SMS via API

You can send an SMS by making a POST request to the `/send-sms` endpoint.

**Example using `curl`**:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"number": "+1234567890", "message": "Hello from the SMS Gateway!"}' \
  http://<your-raspberry-pi-ip>:5000/send-sms
```

This will instruct `gammu-smsd` to send the message.
