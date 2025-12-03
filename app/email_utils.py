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
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import json
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, to_email, from_email=None, from_name=None):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    # Load credentials from environment variable
    token_json_str = os.getenv("TOKEN_JSON")
    creds = Credentials.from_authorized_user_info(json.loads(token_json_str), SCOPES)

    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to_email
    message["from"] = os.getenv("MAIL_FROM")
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_result = service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()

    print(f"Email sent to {to_email}. Message ID: {send_result.get('id')}")
