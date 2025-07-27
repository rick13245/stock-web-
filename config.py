import os
from datetime import datetime, timedelta
import json

class Config:

    
    # Database Configuration
    DATABASE_PATH = "data/stock_data.db"
    HISTORICAL_DATA_PATH = "data/historical/"
    
    # Trading Configuration
    DEFAULT_TIMEFRAME = "1D"  # 1D, 1W, 1M
    MAX_HISTORICAL_YEARS = 25
    SIGNAL_CONFIDENCE_THRESHOLD = 0.7
    
    # Technical Indicators Configuration
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    
    FIBONACCI_LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1, 1.618, 2.618]
    
    # Smart Money Concepts Configuration
    SMC_FAIR_VALUE_GAP_THRESHOLD = 0.02
    SMC_ORDER_BLOCK_THRESHOLD = 0.03
    SMC_LIQUIDITY_SWEEP_THRESHOLD = 0.01
    
    # Risk Management
    MAX_POSITION_SIZE = 0.1  # 10% of portfolio
    STOP_LOSS_PERCENTAGE = 0.02  # 2%
    TAKE_PROFIT_PERCENTAGE = 0.06  # 6%
    
    # Market Hours (IST)
    MARKET_OPEN = "09:15"
    MARKET_CLOSE = "15:30"
    PRE_MARKET_OPEN = "09:00"
    POST_MARKET_CLOSE = "15:45"
    
    # Popular Indian Stocks and Indices
    INDIAN_INDICES = {
        "NIFTY50": "NIFTY 50",
        "BANKNIFTY": "NIFTY BANK",
        "FINNIFTY": "NIFTY FIN SERVICE",
        "SENSEX": "S&P BSE SENSEX"
    }
    
    POPULAR_STOCKS = {
        "RELIANCE": "RELIANCE",
        "TCS": "TCS",
        "HDFCBANK": "HDFC BANK",
        "INFY": "INFOSYS",
        "ICICIBANK": "ICICI BANK",
        "HINDUNILVR": "HINDUNILVR",
        "ITC": "ITC",
        "SBIN": "STATE BANK OF INDIA",
        "BHARTIARTL": "BHARTI AIRTEL",
        "AXISBANK": "AXIS BANK"
    }
    

    

    

    

    
    @classmethod
    def is_market_open(cls):
        """Check if market is currently open"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        return cls.PRE_MARKET_OPEN <= current_time <= cls.POST_MARKET_CLOSE 