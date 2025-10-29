# server-rbpi/api_client.py
import requests
from config import API_SENDO_URL

def add_internal_credits(phone_number, currency, amount, note=""):
    """
    Calls the api-sendo to add internal credits to a user.
    """
    endpoint = f"{API_SENDO_URL}/monitor/internal-credits"
    payload = {
        "phoneNumber": phone_number,
        "currency": currency,
        "amount": amount,
        "note": note or f"SMS deposit from {phone_number}"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        print(f"Successfully added credits for {phone_number}. Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling api-sendo: {e}")
        return None
