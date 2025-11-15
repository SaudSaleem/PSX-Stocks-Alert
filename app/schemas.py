from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    total_investment: Optional[float] = None
    current_value: Optional[float] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AlertCreate(BaseModel):
    ticker: str
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    sl: Optional[float] = None
    percentage_sl: Optional[float] = None
    box_break: Optional[float] = None
    percentage_box_break: Optional[float] = None
    dip_buy: Optional[float] = None
    notes: Optional[str] = None
    buy_price: Optional[float] = None
    shares: Optional[int] = None
    trailing_stop_percentage: Optional[float] = None

class AlertUpdate(BaseModel):
    ticker: str
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    percentage_tp: Optional[float] = None
    sl: Optional[float] = None
    percentage_sl: Optional[float] = None
    box_break: Optional[float] = None
    percentage_box_break: Optional[float] = None
    dip_buy: Optional[float] = None
    notes: Optional[str] = None
    trailing_stop_percentage: Optional[float] = None
    highest_price: Optional[float] = None
    buy_price: Optional[float] = None
    shares: Optional[int] = None 
    is_sl_hit: Optional[bool] = False
    is_tp1_hit: Optional[bool] = False
    is_tp2_hit: Optional[bool] = False
    is_tp3_hit: Optional[bool] = False
    is_box_break_hit: Optional[bool] = False
    is_percentage_sl_hit: Optional[bool] = False
    is_percentage_tp_hit: Optional[bool] = False
    is_trailing_stop_hit: Optional[bool] = False
    is_dip_buy_hit: Optional[bool] = False
    total_alerts_sent: Optional[int] = 0

class InvestmentCreate(BaseModel):
    amount: float
    transaction_type: str = 'add'  # 'add' or 'withdraw'
    description: Optional[str] = None

class PhoneNumberCreate(BaseModel):
    phone_number: str
    label: Optional[str] = None

class PhoneNumberUpdate(BaseModel):
    phone_number: Optional[str] = None
    label: Optional[str] = None
    is_active: Optional[bool] = None

class EmailRecipientCreate(BaseModel):
    email: str
    label: Optional[str] = None

class EmailRecipientUpdate(BaseModel):
    email: Optional[str] = None
    label: Optional[str] = None
    is_active: Optional[bool] = None
