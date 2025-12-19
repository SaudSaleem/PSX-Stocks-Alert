# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587

# # Function to send email
# def send_email(subject: str, body: str, to_email: str, from_email: str, password: str):
#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject

#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(from_email, password)
#         server.sendmail(from_email, to_email, msg.as_string())
#         server.close()
#         print(f"Email sent to {to_email}")
#     except Exception as e:
#         print(f"Failed to send email to {to_email}: {e}") 


import base64
import os
import json
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Google Auth imports
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request # <--- This import is required for refreshing

load_dotenv()

def send_email(subject, body, to_email, from_email=None, from_name=None):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    # 1. Load credentials from environment variable
    token_json_str = os.getenv("TOKEN_JSON")
    
    if not token_json_str:
        print("Error: TOKEN_JSON not found in environment variables.")
        return

    # Load the JSON data
    info = json.loads(token_json_str)
    creds = Credentials.from_authorized_user_info(info, SCOPES)

    # 2. AUTO-REFRESH LOGIC
    # This checks if the access token is expired. 
    # If yes, it uses the 'refresh_token' inside your JSON to get a new one.
    if creds and creds.expired and creds.refresh_token:
        try:
            print("Access token is expired. Refreshing automatically...")
            creds.refresh(Request()) 
            print("Token refreshed successfully.")
            
            # Note: The new token is active in memory for this script run. 
            # Since you are reading from an environment variable, the .env file 
            # itself is NOT updated on disk. This is fine; the script will simply 
            # perform this refresh step again the next time it runs.
            
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            return

    # 3. Build Service and Send Email
    try:
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(body)
        message["to"] = to_email
        
        # Use argument if provided, otherwise fallback to env var
        sender = from_email if from_email else os.getenv("MAIL_FROM")
        message["from"] = sender
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        send_result = service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()

        print(f"Email sent to {to_email}. Message ID: {send_result.get('id')}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage (remove this when putting into production)
# send_email("Hello", "This is a test body", "recipient@example.com")