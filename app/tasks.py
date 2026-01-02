from apscheduler.schedulers.background import BackgroundScheduler
from .crud import get_alerts_by_user_id, update_alert, get_phone_numbers_by_user_id, get_email_recipients_by_user_id
from .email_utils import send_email
from .whatsapp_utils import send_alert_to_multiple, format_alert_message
from .database import SessionLocal
from . import models
from psx import stocks, tickers
from datetime import date, timedelta, datetime
from dotenv import load_dotenv
import os
import json
import time
import traceback
import pytz
load_dotenv()

MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_STARTTLS = os.getenv('MAIL_STARTTLS')

def is_allowed_time_for_sl_and_breakout():
    """
    Check if current time is allowed for SL and breakout notifications and DB updates.
    
    Rules:
    - Monday-Thursday: Before 9:15 AM or after 3:40 PM (Pakistan time)
    - Friday: Before 9:00 AM or after 4:30 PM (Pakistan time)
    - Saturday-Sunday: Allowed all day
    
    Returns:
        bool: True if current time is allowed for SL and breakout alerts, False otherwise
    """
    # Get current time in Pakistan timezone
    pakistan_tz = pytz.timezone('Asia/Karachi')
    now = datetime.now(pytz.UTC).astimezone(pakistan_tz)
    
    weekday = now.weekday()  # Monday=0, Sunday=6
    current_time = (now.hour, now.minute)
    
    # Saturday (5) and Sunday (6) - allowed all day
    if weekday >= 5:
        return True
    
    # Friday (4) - Before 9:00 AM or after 4:30 PM
    if weekday == 4:
        if current_time < (9, 0) or current_time > (16, 30):
            return True
        else:
            print(f"SL and breakout alerts blocked on Friday during trading hours (9:00 AM - 4:30 PM). Current time: {now.strftime('%H:%M')}")
            return False
    
    # Monday-Thursday (0-3) - Before 9:15 AM or after 3:40 PM
    if weekday < 4:
        if current_time < (9, 15) or current_time > (15, 40):
            return True
        else:
            print(f"SL and breakout alerts blocked during trading hours (9:15 AM - 3:40 PM). Current time: {now.strftime('%H:%M')}")
            return False
    
    return True

def get_ticker_by_symbol(ticker: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tickers_path = os.path.join(script_dir, "data", "latest_stock_price.json")
    
    # Check if file exists, if not return empty data
    if not os.path.exists(tickers_path):
        print(f"Warning: {tickers_path} not found. Scraper hasn't run yet.")
        return []
    
    with open(tickers_path, "r") as f:
        data = json.load(f)
    for item in data:
        if item['symbol'] == ticker:
            return item
    return None

def fetch_all_tickers():
    tickersDf = tickers()
    # print('from tasks',tickersDf.loc[0]['symbol'])
    return [{'symbol': ticker['symbol'], 'name': ticker['name']} for _, ticker in tickersDf.iterrows()]

def calculate_percentage_change(current_price, buy_price):
    try:
        if(buy_price == None or buy_price == 0):
            return None
        return round(((current_price - buy_price) / buy_price) * 100, 2)
    except Exception as e:
        print(f"Error in calculate_percentage_change: {e}")
        return None

def check_proximity_alerts(alert, current_price, db, user):
    """
    Check if price is within 2% of SL, TP1, TP2, TP3, Dip Buy 1, or Dip Buy 2
    Priority: SL > Dip Buy 1 > Dip Buy 2 > TP1 > TP2 > TP3
    Only sends one proximity alert per check cycle
    """
    proximity_threshold = 2  # 2% threshold

    
    # Track which proximity alerts have been sent using database flags
    # This prevents sending the same proximity alert repeatedly
    
    # Priority 1: Check Stop Loss proximity
    if alert.sl and not alert.is_sl_hit and not alert.is_sl_proximity_sent:
        # For SL, check if price is going down towards it (within 2% above SL)
        percentage_from_sl = ((current_price - alert.sl) / alert.sl) * 100
        if 0 < percentage_from_sl <= proximity_threshold:
            alert_data = {
                'ticker': alert.ticker,
                'current_price': current_price,
                'alert_type': 'Stop Loss Proximity Warning',
                'trigger_value': alert.sl,
                'change_percentage': alert.change_percentage,
                'notes': alert.notes,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            send_alert_notification(
                db, user, "Stop Loss Proximity",
                "Stop Loss Proximity Alert",
                f"⚠️ IMPORTANT: Stock {alert.ticker} price is close to Stop Loss value of {alert.sl}. Current price: {current_price}. Please set limit order on exchange. Notes: {alert.notes}",
                alert_data
            )
            
            # Mark proximity alert as sent and update database
            alert.is_sl_proximity_sent = True
            alert.total_alerts_sent = alert.total_alerts_sent + 1
            db.commit()
            return True  # Alert sent, don't check others in this cycle
    
    # Priority 2: Check Dip Buy 1 proximity
    if alert.dip_buy and not alert.is_dip_buy_hit and not alert.is_dip_buy_proximity_sent:
        # For Dip Buy 1, check if price is going down towards it (within 2% above Dip Buy)
        percentage_from_dip_buy = ((current_price - alert.dip_buy) / alert.dip_buy) * 100
        print(f"Percentage from Dip Buy 1: {percentage_from_dip_buy}, current price: {current_price}, dip buy: {alert.dip_buy}, proximity threshold: {proximity_threshold}, 0 < percentage_from_dip_buy <= proximity_threshold, {0 < percentage_from_dip_buy <= proximity_threshold}")
        if 0 < percentage_from_dip_buy <= proximity_threshold:
            print(f"Dip Buy 1 proximity alert sent for {alert.ticker}")
            alert_data = {
                'ticker': alert.ticker,
                'current_price': current_price,
                'alert_type': 'Dip Buy 1 Proximity Warning',
                'trigger_value': alert.dip_buy,
                'change_percentage': alert.change_percentage,
                'notes': alert.notes,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            send_alert_notification(
                db, user, "Dip Buy 1 Proximity",
                "Dip Buy 1 Proximity Alert",
                f"💰 OPPORTUNITY: Stock {alert.ticker} price is close to Dip Buy 1 value of {alert.dip_buy}. Current price: {current_price}. Consider setting limit order on exchange. Notes: {alert.notes}",
                alert_data
            )
            
            # Mark proximity alert as sent and update database
            alert.is_dip_buy_proximity_sent = True
            alert.total_alerts_sent = alert.total_alerts_sent + 1
            db.commit()
            return True  # Alert sent, don't check others in this cycle
    
    # Priority 3: Check Dip Buy 2 proximity
    if alert.dip_buy_2 and not alert.is_dip_buy_2_hit and not alert.is_dip_buy_2_proximity_sent:
        # For Dip Buy 2, check if price is going down towards it (within 2% above Dip Buy 2)
        percentage_from_dip_buy_2 = ((current_price - alert.dip_buy_2) / alert.dip_buy_2) * 100
        if 0 < percentage_from_dip_buy_2 <= proximity_threshold:
            alert_data = {
                'ticker': alert.ticker,
                'current_price': current_price,
                'alert_type': 'Dip Buy 2 Proximity Warning',
                'trigger_value': alert.dip_buy_2,
                'change_percentage': alert.change_percentage,
                'notes': alert.notes,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            send_alert_notification(
                db, user, "Dip Buy 2 Proximity",
                "Dip Buy 2 Proximity Alert",
                f"💰 OPPORTUNITY: Stock {alert.ticker} price is close to Dip Buy 2 value of {alert.dip_buy_2}. Current price: {current_price}. Consider setting limit order on exchange. Notes: {alert.notes}",
                alert_data
            )
            
            # Mark proximity alert as sent and update database
            alert.is_dip_buy_2_proximity_sent = True
            alert.total_alerts_sent = alert.total_alerts_sent + 1
            db.commit()
            return True  # Alert sent, don't check others in this cycle
    
    # Priority 4: Check TP1 proximity
    if alert.tp1 and not alert.is_tp1_hit and not alert.is_tp1_proximity_sent:
        # For TP, check if price is going up towards it (within 2% below TP1)
        percentage_from_tp1 = ((alert.tp1 - current_price) / alert.tp1) * 100
        if 0 < percentage_from_tp1 <= proximity_threshold:
            alert_data = {
                'ticker': alert.ticker,
                'current_price': current_price,
                'alert_type': 'Take Profit 1 Proximity Warning',
                'trigger_value': alert.tp1,
                'change_percentage': alert.change_percentage,
                'notes': alert.notes,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            send_alert_notification(
                db, user, "Take Profit 1 Proximity",
                "Take Profit 1 Proximity Alert",
                f"🎯 Stock {alert.ticker} price is close to Take Profit 1 value of {alert.tp1}. Current price: {current_price}. Please set limit order on exchange. Notes: {alert.notes}",
                alert_data
            )
            
            # Mark proximity alert as sent and update database
            alert.is_tp1_proximity_sent = True
            alert.total_alerts_sent = alert.total_alerts_sent + 1
            db.commit()
            return True  # Alert sent, don't check others in this cycle
    
    # Priority 5: Check TP2 proximity
    if alert.tp2 and not alert.is_tp2_hit and not alert.is_tp2_proximity_sent:
        # For TP2, check if price is going up towards it (within 2% below TP2)
        percentage_from_tp2 = ((alert.tp2 - current_price) / alert.tp2) * 100
        if 0 < percentage_from_tp2 <= proximity_threshold:
            alert_data = {
                'ticker': alert.ticker,
                'current_price': current_price,
                'alert_type': 'Take Profit 2 Proximity Warning',
                'trigger_value': alert.tp2,
                'change_percentage': alert.change_percentage,
                'notes': alert.notes,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            send_alert_notification(
                db, user, "Take Profit 2 Proximity",
                "Take Profit 2 Proximity Alert",
                f"🎯 Stock {alert.ticker} price is close to Take Profit 2 value of {alert.tp2}. Current price: {current_price}. Please set limit order on exchange. Notes: {alert.notes}",
                alert_data
            )
            
            # Mark proximity alert as sent and update database
            alert.is_tp2_proximity_sent = True
            alert.total_alerts_sent = alert.total_alerts_sent + 1
            db.commit()
            return True  # Alert sent, don't check others in this cycle
    
    # Priority 6: Check TP3 proximity
    if alert.tp3 and not alert.is_tp3_hit and not alert.is_tp3_proximity_sent:
        # For TP3, check if price is going up towards it (within 2% below TP3)
        percentage_from_tp3 = ((alert.tp3 - current_price) / alert.tp3) * 100
        if 0 < percentage_from_tp3 <= proximity_threshold:
            alert_data = {
                'ticker': alert.ticker,
                'current_price': current_price,
                'alert_type': 'Take Profit 3 Proximity Warning',
                'trigger_value': alert.tp3,
                'change_percentage': alert.change_percentage,
                'notes': alert.notes,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            send_alert_notification(
                db, user, "Take Profit 3 Proximity",
                "Take Profit 3 Proximity Alert",
                f"🎯 Stock {alert.ticker} price is close to Take Profit 3 value of {alert.tp3}. Current price: {current_price}. Please set limit order on exchange. Notes: {alert.notes}",
                alert_data
            )
            
            # Mark proximity alert as sent and update database
            alert.is_tp3_proximity_sent = True
            alert.total_alerts_sent = alert.total_alerts_sent + 1
            db.commit()
            return True  # Alert sent, don't check others in this cycle
    
    return False  # No proximity alert sent

# Function to fetch stock price
# def fetch_stock_price(stock_name: str):
#     try:
#         start_date = date.today() - timedelta(days=1)
#         end_date = date.today()
#         data = stocks(stock_name, start=start_date, end=end_date)
#         latest_data = data.iloc[-1]  # Get the latest available data
#         return latest_data['Close']
#     except Exception as e:
#         print(f"Error fetching stock price for {stock_name}: {e}")
#         return None

def fetch_stock_price(stock_name: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tickers_path = os.path.join(script_dir, "data", "latest_stock_price.json")
    
    # Check if file exists, if not return None
    if not os.path.exists(tickers_path):
        print(f"Warning: {tickers_path} not found. Scraper hasn't run yet.")
        return None
    
    with open(tickers_path, "r") as f:
        data = json.load(f)
    for item in data:
        if item['symbol'] == stock_name:
            return {
                'symbol': item['symbol'],
                'name': item['name'],
                'ldcp': item['ldcp'],
                'open': item['open'],
                'high': item['high'],
                'low': item['low'],
                'current': item['current']
            }
    return None

def send_alert_notification(db, user, alert_type, email_subject, email_body, alert_data):
    """
    Helper function to send alerts via both email and WhatsApp based on user preferences
    
    Args:
        db: Database session
        user: User object
        alert_type: Type of alert (for formatting)
        email_subject: Subject for email
        email_body: Body for email
        alert_data: Dictionary with alert information for WhatsApp formatting
    """
    wait_time = 20
    time.sleep(wait_time)
    print(f"Waiting for {wait_time} seconds before sending alert notification...")
    # Send emails only if email notifications are enabled
    if user.email_notifications_enabled:
        try:
            email_recipients = get_email_recipients_by_user_id(db, user.id, active_only=True)
            if email_recipients and len(email_recipients) > 0:
                for recipient in email_recipients:
                    try:
                        send_email(email_subject, email_body, recipient.email, MAIL_FROM, MAIL_PASSWORD)
                        print(f"Email sent successfully to {recipient.email}")
                    except Exception as e:
                        print(f"Error sending email to {recipient.email}: {e}")
            else:
                # Fallback to user's login email if no recipients are registered
                try:
                    send_email(email_subject, email_body, user.email, MAIL_FROM, MAIL_PASSWORD)
                    print(f"Email sent to user's login email: {user.email}")
                except Exception as e:
                    print(f"Error sending email to {user.email}: {e}")
        except Exception as e:
            print(f"Error fetching email recipients: {e}")
    else:
        print(f"Email notifications disabled for user {user.email}")
    
    # Send WhatsApp messages only if WhatsApp notifications are enabled
    if user.whatsapp_notifications_enabled:
        try:
            phone_numbers = get_phone_numbers_by_user_id(db, user.id, active_only=True)
            if phone_numbers and len(phone_numbers) > 0:
                phone_list = [phone.phone_number for phone in phone_numbers]
                whatsapp_message = format_alert_message(alert_data)
                result = send_alert_to_multiple(phone_list, whatsapp_message)
                print(f"WhatsApp alerts sent: {result['successful']}/{result['total']}")
            else:
                print(f"No active phone numbers found for user {user.email}")
        except Exception as e:
            print(f"Error sending WhatsApp alerts: {e}")
    else:
        print(f"WhatsApp notifications disabled for user {user.email}")

# Function to check alerts
def check_alerts():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        for user in users:
            alerts = get_alerts_by_user_id(db, user.id)
            # print('in check_alerts method: alerts', alerts)
            for alert in alerts:
                # 1. Fetch stock data
                stock_data = fetch_stock_price(alert.ticker)
                
                if stock_data is None:
                    print(f'Stock price for {alert.ticker} not found, skipping...')
                    continue

                stock_price = stock_data['current']
                stock_today_high = stock_data['high']
                stock_today_low = stock_data['low']
                # stock_today_open = stock_data['open'] 
                
                try:
                    current_price = float(stock_price)
                    today_high = float(stock_today_high)
                    today_low = float(stock_today_low)
                except (ValueError, TypeError) as e:
                    print(f'Error converting stock price for {alert.ticker}: {e}, skipping...')
                    continue

                print(f'Checking {alert.ticker}: Current: {current_price}, High: {today_high}, Low: {today_low}')
                
                # 2. Update highest price for trailing stop (Only uses current price to avoid false triggering on old highs)
                if alert.trailing_stop_percentage and (alert.highest_price is None or current_price > alert.highest_price):
                    alert.highest_price = current_price
                    db.commit()
                
                # 3. Update percentage tracking
                alert.change_percentage = calculate_percentage_change(current_price, alert.buy_price)
                alert.current_price = current_price
                db.commit()
                
                # 4. Check proximity alerts (1.5% - 2% near to SL, TP1, TP2, TP3)
                # We check this first, but if a hard alert is hit below, the hard alert takes precedence in logic flow usually
                check_proximity_alerts(alert, current_price, db, user)
                
                # --- ALERT CONDITION CHECKS ---

                # A. Check Trailing Stop (Strictly uses Current Price)
                if (alert.is_trailing_stop_hit == False and 
                    alert.trailing_stop_percentage and 
                    alert.highest_price and 
                    current_price < alert.highest_price * (1 - alert.trailing_stop_percentage / 100)):
                    
                    drop_percentage = round(((alert.highest_price - current_price) / alert.highest_price) * 100, 2)
                    
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Trailing Stop',
                        'trigger_value': alert.highest_price,
                        'change_percentage': f"-{drop_percentage}",
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Trailing Stop",
                        "Trailing Stop Alert",
                        f"Trailing Stop hit. The stock {alert.ticker} has dropped {drop_percentage}% from its highest price of {alert.highest_price}. Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_trailing_stop_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                
                # B. Check Dip Buy 1 (Uses Day Low - if it touched, we want to know)
                elif alert.is_dip_buy_hit == False and alert.dip_buy and today_low <= alert.dip_buy:
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Dip Buy 1',
                        'trigger_value': alert.dip_buy,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Dip Buy 1",
                        "Dip Buy 1 Alert",
                        f"The stock {alert.ticker} reached your dip buy 1 price of {alert.dip_buy} (Day Low: {today_low}). Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_dip_buy_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                
                # C. Check Dip Buy 2 (Uses Day Low)
                elif alert.is_dip_buy_2_hit == False and alert.dip_buy_2 and today_low <= alert.dip_buy_2:
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Dip Buy 2',
                        'trigger_value': alert.dip_buy_2,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Dip Buy 2",
                        "Dip Buy 2 Alert",
                        f"The stock {alert.ticker} reached your dip buy 2 price of {alert.dip_buy_2} (Day Low: {today_low}). Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_dip_buy_2_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                
                # D. Check Stop Loss (Uses Day Low)
                # Only allow SL notifications and DB updates outside trading hours
                elif alert.is_sl_hit == False and alert.sl and today_low <= alert.sl and is_allowed_time_for_sl_and_breakout():
                    # Distinguish between currently below SL vs. "Wick" touched SL
                    if current_price <= alert.sl:
                        subject = "Stop Loss Alert (EXECUTED)"
                        body_prefix = f"URGENT: The stock {alert.ticker} is trading BELOW your stop loss price: {alert.sl}."
                    else:
                        subject = "Stop Loss Alert (TOUCHED)"
                        body_prefix = f"WARNING: The stock {alert.ticker} touched your stop loss price of {alert.sl} (Day Low: {today_low}) but recovered to {current_price}."

                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Stop Loss',
                        'trigger_value': alert.sl,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Stop Loss",
                        subject,
                        f"{body_prefix} Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_sl_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()

                # E. Check TP1 (Uses Day High)
                elif alert.is_tp1_hit == False and alert.tp1 and today_high >= alert.tp1:
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Take Profit Level 1',
                        'trigger_value': alert.tp1,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Take Profit",
                        "Take Profit Alert",
                        f"The stock {alert.ticker} hit take profit level 1: {alert.tp1} (Day High: {today_high}). SL updated to buy price {alert.buy_price}. Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.sl = alert.buy_price
                    alert.is_sl_hit = False
                    alert.is_tp1_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()

                # F. Check TP2 (Uses Day High)
                elif alert.is_tp2_hit == False and alert.tp2 and today_high >= alert.tp2:
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Take Profit Level 2',
                        'trigger_value': alert.tp2,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Take Profit",
                        "Take Profit Alert",
                        f"The stock {alert.ticker} hit take profit level 2: {alert.tp2} (Day High: {today_high}). SL updated to TP1 {alert.tp1}. Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.sl = alert.tp1
                    alert.is_sl_hit = False
                    alert.is_tp2_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()

                # G. Check TP3 (Uses Day High)
                elif alert.is_tp3_hit == False and alert.tp3 and today_high >= alert.tp3:
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Take Profit Level 3',
                        'trigger_value': alert.tp3,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Take Profit",
                        "Take Profit Alert",
                        f"The stock {alert.ticker} hit take profit level 3: {alert.tp3} (Day High: {today_high}). SL updated to TP2 {alert.tp2}. Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.sl = alert.tp2
                    alert.is_sl_hit = False
                    alert.is_tp3_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                    
                # H. Check Box Break (Uses Day High)
                # Only allow breakout notifications and DB updates outside trading hours
                elif alert.is_box_break_hit == False and alert.box_break and today_high >= alert.box_break and is_allowed_time_for_sl_and_breakout():
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Box Break',
                        'trigger_value': alert.box_break,
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Box Break",
                        "Box Break Alert",
                        f"The stock {alert.ticker} hit the box break price {alert.box_break} (Day High: {today_high}). Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_box_break_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                    
                # I. Check Percentage TP
                elif alert.is_percentage_tp_hit == False and alert.percentage_tp and alert.change_percentage >= alert.percentage_tp:
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Percentage Take Profit',
                        'trigger_value': f"{alert.percentage_tp}%",
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Take Profit",
                        "Take Profit Alert for percentage",
                        f"The stock {alert.ticker} has hit the take profit level {alert.percentage_tp}%. Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_percentage_tp_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                    
                # J. Check Percentage SL
                elif alert.is_percentage_sl_hit == False and alert.percentage_sl and alert.change_percentage <= -abs(alert.percentage_sl):
                    alert_data = {
                        'ticker': alert.ticker,
                        'current_price': current_price,
                        'alert_type': 'Percentage Stop Loss',
                        'trigger_value': f"{alert.percentage_sl}%",
                        'change_percentage': alert.change_percentage,
                        'notes': alert.notes,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    send_alert_notification(
                        db, user, "Stop Loss",
                        "Stop Loss Alert for percentage",
                        f"The stock {alert.ticker} has hit the percentage stop loss level {alert.percentage_sl}%. Current price: {current_price}, Notes: {alert.notes}",
                        alert_data
                    )
                    
                    alert.is_percentage_sl_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                    
    except Exception as e:
        db.rollback()
        print(f"Error in check_alerts: {e}")
        traceback.print_exc() 
    finally:
        db.close()

# Scheduler setup
# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(check_alerts, 'interval', minutes=1)
#     scheduler.start() 