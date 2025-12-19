from sqlalchemy.orm import Session
from . import models, schemas
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, password=user.password, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get user by email
def get_user_by_email(db: Session, email: str):
    try:
        print(f"Getting user by email: {email}")
        return db.query(models.User).filter(models.User.email == email).first()
    except Exception as e:
        raise

# Create a new alert
def create_alert(db: Session, alert: schemas.AlertCreate, user_id: int):
    db_alert = models.Alert(**alert.model_dump(), user_id=user_id)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

# Get alerts by user_id
def get_alerts_by_user_id(db: Session, user_id: int):
    return db.query(models.Alert).filter(models.Alert.user_id == user_id).all()

# Update an alert
def update_alert(db: Session, db_alert: models.Alert):
    try:
        db.commit()
        db.refresh(db_alert)
        return db_alert
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise

# Delete an alert
def delete_alert(db: Session, alert_id: int):
    try:
        db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
        db.delete(db_alert)
        db.commit() 
        return db_alert
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise

# get all users
def _get_all_users(db: Session):
    return db.query(models.User).all()

# Create a new investment
def create_investment(db: Session, investment: schemas.InvestmentCreate, user_id: int):
    db_investment = models.Investment(**investment.model_dump(), user_id=user_id)
    db.add(db_investment)
    
    # Update user's total investment
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        if investment.transaction_type == 'add':
            user.total_investment = (user.total_investment or 0) + investment.amount
        elif investment.transaction_type == 'withdraw':
            user.total_investment = (user.total_investment or 0) - investment.amount
    
    db.commit()
    db.refresh(db_investment)
    return db_investment

# Get investments by user_id
def get_investments_by_user_id(db: Session, user_id: int):
    return db.query(models.Investment).filter(models.Investment.user_id == user_id).all()

# Calculate portfolio value and P&L
def calculate_portfolio_pnl(db: Session, user_id: int):
    """
    Returns portfolio P&L based on manually saved values.
    No automatic calculations - uses user's manually entered current_value.
    Only calculates invested_in_shares based on alerts with shares.
    """
    # Get all alerts for the user
    alerts = db.query(models.Alert).filter(models.Alert.user_id == user_id).all()
    
    # Calculate amount invested in shares (cost basis)
    total_invested_in_shares = 0
    
    for alert in alerts:
        # Only consider alerts where shares have actually been bought
        # Alerts with no shares or no buy_price are just watchlist/monitoring alerts
        if alert.shares and alert.shares > 0 and alert.buy_price and alert.buy_price > 0:
            # Calculate cost basis (amount invested)
            total_invested_in_shares += alert.shares * alert.buy_price
    
    # Get user with manually saved values
    user = db.query(models.User).filter(models.User.id == user_id).first()
    total_investment = user.total_investment if user else 0
    current_value = user.current_value if user else 0
    
    # Calculate cash available (total investment minus what's invested in shares)
    cash_available = total_investment - total_invested_in_shares
    
    # Calculate P&L based on manually saved current_value
    pnl = current_value - total_investment
    pnl_percentage = (pnl / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "total_investment": total_investment,
        "invested_in_shares": total_invested_in_shares,
        "cash_available": cash_available,
        "current_value": current_value,
        "pnl": pnl,
        "pnl_percentage": pnl_percentage
    }

# Phone Number CRUD operations
def create_phone_number(db: Session, phone_number: schemas.PhoneNumberCreate, user_id: int):
    db_phone = models.PhoneNumber(**phone_number.model_dump(), user_id=user_id)
    db.add(db_phone)
    db.commit()
    db.refresh(db_phone)
    return db_phone

def get_phone_numbers_by_user_id(db: Session, user_id: int, active_only: bool = True):
    query = db.query(models.PhoneNumber).filter(models.PhoneNumber.user_id == user_id)
    if active_only:
        query = query.filter(models.PhoneNumber.is_active == True)
    return query.all()

def update_phone_number(db: Session, phone_id: int, phone_update: schemas.PhoneNumberUpdate):
    try:
        db_phone = db.query(models.PhoneNumber).filter(models.PhoneNumber.id == phone_id).first()
        if not db_phone:
            return None
            
        for key, value in phone_update.model_dump(exclude_unset=True).items():
            setattr(db_phone, key, value)
            
        db.commit()
        db.refresh(db_phone)
        return db_phone
    except Exception as e:
        db.rollback()
        logger.error(f"An error occurred: {e}")
        raise

def delete_phone_number(db: Session, phone_id: int):
    try:
        db_phone = db.query(models.PhoneNumber).filter(models.PhoneNumber.id == phone_id).first()
        if not db_phone:
            return None
        db.delete(db_phone)
        db.commit()
        return db_phone
    except Exception as e:
        db.rollback()
        logger.error(f"An error occurred: {e}")
        raise

# Email Recipient CRUD operations
def create_email_recipient(db: Session, email_recipient: schemas.EmailRecipientCreate, user_id: int):
    db_email = models.EmailRecipient(**email_recipient.model_dump(), user_id=user_id)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def get_email_recipients_by_user_id(db: Session, user_id: int, active_only: bool = True):
    query = db.query(models.EmailRecipient).filter(models.EmailRecipient.user_id == user_id)
    if active_only:
        query = query.filter(models.EmailRecipient.is_active == True)
    return query.all()

def update_email_recipient(db: Session, email_id: int, email_update: schemas.EmailRecipientUpdate):
    try:
        db_email = db.query(models.EmailRecipient).filter(models.EmailRecipient.id == email_id).first()
        if not db_email:
            return None
            
        for key, value in email_update.model_dump(exclude_unset=True).items():
            setattr(db_email, key, value)
            
        db.commit()
        db.refresh(db_email)
        return db_email
    except Exception as e:
        db.rollback()
        logger.error(f"An error occurred: {e}")
        raise

def delete_email_recipient(db: Session, email_id: int):
    try:
        db_email = db.query(models.EmailRecipient).filter(models.EmailRecipient.id == email_id).first()
        if not db_email:
            return None
        db.delete(db_email)
        db.commit()
        return db_email
    except Exception as e:
        db.rollback()
        logger.error(f"An error occurred: {e}")
        raise

# Notification Preferences CRUD operations
def update_notification_preferences(db: Session, user_id: int, preferences: schemas.NotificationPreferencesUpdate):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return None
            
        for key, value in preferences.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
            
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"An error occurred: {e}")
        raise