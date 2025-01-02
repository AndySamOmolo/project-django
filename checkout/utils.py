import requests
import os
import json
from datetime import datetime
import base64
from django.conf import settings
from decimal import Decimal

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), headers=headers)
    try:
        return response.json()['access_token']
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error getting access token: {e}, Response: {response.text}")
        return None

def generate_password():
    # Get the current timestamp in the required format (yyyyMMddHHmmss)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # Concatenate Business Short Code, PassKey, and Timestamp
    password_string = f"{settings.MPESA_BUSINESS_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"

    # Base64 encode the string
    encoded_password = base64.b64encode(password_string.encode('utf-8')).decode('utf-8')

    return encoded_password

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    access_token = get_access_token()
    print(f"Access token: {access_token}")

    if access_token is None:
        return {"error": "Failed to get access token"}

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    # Ensure the amount is a valid integer (representing the full amount, not cents)
    try:
        amount = int(Decimal(amount))  # Convert to integer without multiplying by 100
    except (ValueError, TypeError) as e:
        return {"error": f"Invalid amount format: {e}"}

    print(f"Converted Amount: {amount}")  # This will now print 50 if the amount is 50.00

    # Generate timestamp and password
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_password()

    payload = {
        "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,  # Amount is now in whole units (e.g., 50)
        "PartyA": phone_number,
        "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response_json = response.json()  # Get the response as JSON
        print("API Response:", json.dumps(response_json, indent=4))  # Pretty-print the raw response
        
        return response_json
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON decoding error: {e}"}

