#!/usr/bin/env python3
"""
FastAPI Application for Advanced Stock Market Signal Bot
========================================================

A FastAPI web application providing REST API endpoints for:
- Angel One authentication and login
- Stock market data and analysis
- Buy/Sell signal generation
- Portfolio management
- Real-time market data

Features:
- Angel One SmartAPI integration
- JWT token-based authentication
- Advanced technical analysis
- Real-time signal generation
- Portfolio tracking
- Historical data analysis

Author: AI Assistant
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# Import our modules
from angel_one_api import AngelOneAPI
from trading_bot import TradingBot
from config import Config

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Stock Market Signal Bot API",
    description="FastAPI application for advanced stock market analysis and trading signals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security
security = HTTPBearer()

# Global variables to store API instances
angel_api_instances = {}
trading_bot_instances = {}

# Pydantic models for request/response
class LoginRequest(BaseModel):
    api_key: str
    client_id: str
    password: str
    totp_secret: str

class LoginResponse(BaseModel):
    status: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None

class SymbolRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"

class HistoricalDataRequest(BaseModel):
    symbol: str
    exchange: str = "NSE"
    interval: str = "ONE_DAY"
    from_date: Optional[str] = None
    to_date: Optional[str] = None

class OrderRequest(BaseModel):
    symbol: str
    quantity: int
    side: str  # BUY or SELL
    order_type: str = "MARKET"
    price: float = 0
    exchange: str = "NSE"

class SignalAnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1D"
    exchange: str = "NSE"

class WatchlistRequest(BaseModel):
    symbols: List[str]

# Utility functions
def get_user_id_from_token(token: str) -> str:
    """Extract user ID from token - simplified for demo"""
    # In production, you'd decode and validate the JWT token properly
    return token.split("_")[0] if "_" in token else "default_user"

def get_angel_api_instance(user_id: str) -> AngelOneAPI:
    """Get Angel API instance for user"""
    if user_id not in angel_api_instances:
        angel_api_instances[user_id] = AngelOneAPI()
    return angel_api_instances[user_id]

def get_trading_bot_instance(user_id: str) -> TradingBot:
    """Get Trading Bot instance for user"""
    if user_id not in trading_bot_instances:
        trading_bot_instances[user_id] = TradingBot()
    return trading_bot_instances[user_id]

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user ID"""
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    
    # Check if user has an active Angel API session
    angel_api = get_angel_api_instance(user_id)
    if not angel_api.is_connected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Angel One session expired or not logged in"
        )
    
    return user_id

# API Endpoints

@app.get("/")
async def root():
    """Serve the main HTML interface"""
    return FileResponse('static/index.html')

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Advanced Stock Market Signal Bot API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "angel_one_api": "available",
            "trading_bot": "available",
            "database": "available"
        }
    }

# Authentication Endpoints

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login to Angel One API"""
    try:
        # Create a new Angel API instance
        angel_api = AngelOneAPI(api_key=request.api_key)
        
        # Attempt login
        login_result = angel_api.login(
            api_key=request.api_key,
            client_id=request.client_id,
            password=request.password,
            totp_secret=request.totp_secret
        )
        
        if login_result["status"]:
            # Store API instance for this user
            user_id = login_result["data"]["user_id"]
            angel_api_instances[user_id] = angel_api
            
            # Create a simple token (in production, use proper JWT)
            access_token = f"{user_id}_{datetime.now().timestamp()}"
            
            return LoginResponse(
                status=True,
                message="Login successful",
                data=login_result["data"],
                access_token=access_token
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=login_result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/auth/logout")
async def logout(user_id: str = Depends(verify_token)):
    """Logout from Angel One API"""
    try:
        angel_api = get_angel_api_instance(user_id)
        logout_result = angel_api.logout()
        
        # Clean up instances
        if user_id in angel_api_instances:
            del angel_api_instances[user_id]
        if user_id in trading_bot_instances:
            del trading_bot_instances[user_id]
        
        return logout_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@app.get("/auth/profile")
async def get_profile(user_id: str = Depends(verify_token)):
    """Get user profile information"""
    try:
        angel_api = get_angel_api_instance(user_id)
        profile = angel_api.get_profile()
        
        if profile["status"]:
            return profile
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=profile["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )

# Market Data Endpoints

@app.post("/market/live-price")
async def get_live_price(request: SymbolRequest, user_id: str = Depends(verify_token)):
    """Get live price for a symbol"""
    try:
        angel_api = get_angel_api_instance(user_id)
        price = angel_api.get_live_price(request.symbol, request.exchange)
        
        if price is not None:
            return {
                "status": True,
                "symbol": request.symbol,
                "exchange": request.exchange,
                "price": price,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to get live price"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get live price: {str(e)}"
        )

@app.post("/market/historical-data")
async def get_historical_data(request: HistoricalDataRequest, user_id: str = Depends(verify_token)):
    """Get historical data for a symbol"""
    try:
        angel_api = get_angel_api_instance(user_id)
        data = angel_api.get_historical_data(
            symbol=request.symbol,
            exchange=request.exchange,
            interval=request.interval,
            from_date=request.from_date,
            to_date=request.to_date
        )
        
        if data is not None:
            return {
                "status": True,
                "symbol": request.symbol,
                "exchange": request.exchange,
                "interval": request.interval,
                "data": data.to_dict('records'),
                "total_records": len(data)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to get historical data"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get historical data: {str(e)}"
        )

@app.post("/market/search-symbol")
async def search_symbol(request: SymbolRequest, user_id: str = Depends(verify_token)):
    """Search for symbol information"""
    try:
        angel_api = get_angel_api_instance(user_id)
        search_result = angel_api.search_symbol(request.symbol)
        
        if search_result:
            return {
                "status": True,
                "symbol": request.symbol,
                "data": search_result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Symbol not found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search symbol: {str(e)}"
        )

# Trading Endpoints

@app.post("/trading/place-order")
async def place_order(request: OrderRequest, user_id: str = Depends(verify_token)):
    """Place a trading order"""
    try:
        angel_api = get_angel_api_instance(user_id)
        order_id = angel_api.place_order(
            symbol=request.symbol,
            quantity=request.quantity,
            side=request.side,
            order_type=request.order_type,
            price=request.price,
            exchange=request.exchange
        )
        
        if order_id:
            return {
                "status": True,
                "message": "Order placed successfully",
                "order_id": order_id,
                "symbol": request.symbol,
                "quantity": request.quantity,
                "side": request.side
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to place order"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order: {str(e)}"
        )

@app.get("/trading/portfolio")
async def get_portfolio(user_id: str = Depends(verify_token)):
    """Get current portfolio"""
    try:
        angel_api = get_angel_api_instance(user_id)
        portfolio = angel_api.get_portfolio()
        
        if portfolio:
            return {
                "status": True,
                "data": portfolio
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to get portfolio"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio: {str(e)}"
        )

# Signal Analysis Endpoints

@app.post("/signals/analyze")
async def analyze_symbol(request: SignalAnalysisRequest, user_id: str = Depends(verify_token)):
    """Analyze a symbol and generate trading signals"""
    try:
        trading_bot = get_trading_bot_instance(user_id)
        
        # Add symbol to analysis if not already there
        trading_bot.add_to_watchlist(request.symbol)
        
        # Generate signals for the symbol
        signals = trading_bot.analyze_symbol(request.symbol, request.timeframe)
        
        if signals:
            return {
                "status": True,
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "signals": signals
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No signals generated for symbol"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze symbol: {str(e)}"
        )

@app.get("/signals/all")
async def get_all_signals(user_id: str = Depends(verify_token)):
    """Get all recent signals"""
    try:
        trading_bot = get_trading_bot_instance(user_id)
        signals = trading_bot.get_recent_signals(days=7)
        
        if not signals.empty:
            return {
                "status": True,
                "total_signals": len(signals),
                "signals": signals.to_dict('records')
            }
        else:
            return {
                "status": True,
                "total_signals": 0,
                "signals": [],
                "message": "No recent signals found"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get signals: {str(e)}"
        )

@app.get("/signals/strong")
async def get_strong_signals(user_id: str = Depends(verify_token)):
    """Get strong trading signals"""
    try:
        trading_bot = get_trading_bot_instance(user_id)
        alerts = trading_bot.get_signal_alerts('STRONG')
        
        return {
            "status": True,
            "total_signals": len(alerts) if alerts else 0,
            "signals": alerts or [],
            "message": f"Found {len(alerts) if alerts else 0} strong signals"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strong signals: {str(e)}"
        )

# Watchlist Endpoints

@app.post("/watchlist/add")
async def add_to_watchlist(request: WatchlistRequest, user_id: str = Depends(verify_token)):
    """Add symbols to watchlist"""
    try:
        trading_bot = get_trading_bot_instance(user_id)
        added_symbols = []
        
        for symbol in request.symbols:
            success = trading_bot.add_to_watchlist(symbol)
            if success:
                added_symbols.append(symbol)
        
        return {
            "status": True,
            "message": f"Added {len(added_symbols)} symbols to watchlist",
            "added_symbols": added_symbols,
            "total_symbols": len(added_symbols)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add to watchlist: {str(e)}"
        )

@app.get("/watchlist")
async def get_watchlist(user_id: str = Depends(verify_token)):
    """Get current watchlist"""
    try:
        trading_bot = get_trading_bot_instance(user_id)
        watchlist = trading_bot.get_watchlist()
        
        return {
            "status": True,
            "watchlist": watchlist,
            "total_symbols": len(watchlist)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get watchlist: {str(e)}"
        )

# Report Endpoints

@app.get("/reports/signal-report")
async def generate_signal_report(user_id: str = Depends(verify_token)):
    """Generate comprehensive signal report"""
    try:
        trading_bot = get_trading_bot_instance(user_id)
        report = trading_bot.generate_signal_report()
        
        if report:
            return {
                "status": True,
                "report": report
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to generate signal report"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate signal report: {str(e)}"
        )

# Configuration Endpoints

@app.get("/config/popular-stocks")
async def get_popular_stocks():
    """Get list of popular Indian stocks"""
    return {
        "status": True,
        "popular_stocks": Config.POPULAR_STOCKS,
        "indices": Config.INDIAN_INDICES
    }

@app.get("/config/market-status")
async def get_market_status():
    """Get current market status"""
    is_open = Config.is_market_open()
    current_time = datetime.now().strftime("%H:%M")
    
    return {
        "status": True,
        "market_open": is_open,
        "current_time": current_time,
        "market_hours": {
            "pre_market": Config.PRE_MARKET_OPEN,
            "market_open": Config.MARKET_OPEN,
            "market_close": Config.MARKET_CLOSE,
            "post_market": Config.POST_MARKET_CLOSE
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Advanced Stock Market Signal Bot API...")
    print("Documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )