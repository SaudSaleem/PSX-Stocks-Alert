from twilio.rest import Client
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

def get_twilio_client():
    """Initialize and return Twilio client"""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.error("Twilio credentials not configured")
        return None
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {str(e)}")
        return None

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """
    Send a WhatsApp message using Twilio
    
    Args:
        to_number: Recipient phone number in format: whatsapp:+1234567890 or +1234567890
        message: Message content to send
        
    Returns:
        dict with 'success' boolean and 'message_sid' or 'error'
    """
    client = get_twilio_client()
    
    if not client:
        return {
            'success': False,
            'error': 'Twilio client not configured'
        }
    
    # Ensure phone number has whatsapp: prefix
    if not to_number.startswith('whatsapp:'):
        to_number = f'whatsapp:{to_number}'
    
    try:
        message_obj = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=message,
            to=to_number
        )
        
        logger.info(f"WhatsApp message sent successfully. SID: {message_obj.sid}")
        
        return {
            'success': True,
            'message_sid': message_obj.sid,
            'status': message_obj.status
        }
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def send_alert_to_multiple(phone_numbers: list, message: str) -> dict:
    """
    Send alert message to multiple WhatsApp numbers
    
    Args:
        phone_numbers: List of phone numbers
        message: Alert message content
        
    Returns:
        dict with 'total', 'successful', 'failed' counts and 'results' list
    """
    results = []
    successful = 0
    failed = 0
    
    for phone_number in phone_numbers:
        result = send_whatsapp_message(phone_number, message)
        
        if result['success']:
            successful += 1
        else:
            failed += 1
            
        results.append({
            'phone_number': phone_number,
            'result': result
        })
    
    return {
        'total': len(phone_numbers),
        'successful': successful,
        'failed': failed,
        'results': results
    }

def format_alert_message(alert_data: dict) -> str:
    """
    Format alert data into a readable WhatsApp message
    
    Args:
        alert_data: Dictionary containing alert information
        
    Returns:
        Formatted message string
    """
    ticker = alert_data.get('ticker', 'N/A')
    current_price = alert_data.get('current_price', 'N/A')
    alert_type = alert_data.get('alert_type', 'Alert')
    trigger_value = alert_data.get('trigger_value', 'N/A')
    change_percentage = alert_data.get('change_percentage', 'N/A')
    
    message = f"""
🚨 *Stock Alert: {ticker}* 🚨

📊 Alert Type: {alert_type}
💰 Current Price: PKR {current_price}
🎯 Trigger Value: PKR {trigger_value}
📈 Change: {change_percentage}%

⏰ Time: {alert_data.get('time', 'Now')}
    """.strip()
    
    # Add notes if available
    if alert_data.get('notes'):
        message += f"\n\n📝 Notes: {alert_data.get('notes')}"
    
    return message

