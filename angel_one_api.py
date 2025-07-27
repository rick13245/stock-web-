import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'smartapi-python'))

from SmartApi import SmartConnect
import pandas as pd
from datetime import datetime, timedelta
import pyotp
from config import Config

class AngelOneAPI:
    def __init__(self, api_key=None):
        """Initialize Angel One API with optional API key"""
        self.api_key = api_key
        self.smart_api = None
        self.access_token = None
        self.refresh_token = None
        self.feed_token = None
        self.user_id = None
        self.is_connected = False
        
    def generate_totp(self, totp_secret):
        """Generate TOTP from secret key"""
        try:
            totp = pyotp.TOTP(totp_secret)
            return totp.now()
        except Exception as e:
            print(f"Error generating TOTP: {e}")
            return None
    
    def login(self, api_key, client_id, password, totp_secret):
        """Login to Angel One API using SmartConnect"""
        try:
            # Initialize SmartConnect
            self.smart_api = SmartConnect(api_key=api_key)
            
            # Generate TOTP
            totp = self.generate_totp(totp_secret)
            if not totp:
                return {"status": False, "message": "Failed to generate TOTP"}
            
            # Login using generateSession
            data = self.smart_api.generateSession(client_id, password, totp)
            
            if data.get('status'):
                # Extract tokens and user info
                self.access_token = data['data']['jwtToken']
                self.refresh_token = data['data']['refreshToken']
                self.feed_token = data['data']['feedToken']
                self.user_id = data['data']['clientcode']
                self.is_connected = True
                
                return {
                    "status": True,
                    "message": "Login successful",
                    "data": {
                        "user_id": self.user_id,
                        "client_name": data['data'].get('clientname', ''),
                        "email": data['data'].get('email', ''),
                        "mobile": data['data'].get('mobileno', '')
                    }
                }
            else:
                return {
                    "status": False,
                    "message": data.get('message', 'Login failed'),
                    "error": data.get('errorcode', '')
                }
                
        except Exception as e:
            print(f"Login error: {e}")
            return {
                "status": False,
                "message": f"Login failed: {str(e)}"
            }
    
    def get_profile(self):
        """Get user profile information"""
        try:
            if not self.is_connected or not self.smart_api:
                return {"status": False, "message": "Not connected to Angel One API"}
            
            profile = self.smart_api.getProfile(self.refresh_token)
            
            if profile.get('status'):
                return {
                    "status": True,
                    "data": profile['data']
                }
            else:
                return {
                    "status": False,
                    "message": profile.get('message', 'Failed to get profile')
                }
                
        except Exception as e:
            print(f"Error getting profile: {e}")
            return {"status": False, "message": f"Error getting profile: {str(e)}"}
    
    def get_historical_data(self, symbol, exchange="NSE", interval="ONE_DAY", from_date=None, to_date=None):
        """Get historical data for a symbol"""
        try:
            if not self.is_connected or not self.smart_api:
                return None
            
            if from_date is None:
                from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M")
            if to_date is None:
                to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Get symbol token (this would need to be implemented with proper symbol mapping)
            symbol_token = self.get_symbol_token(symbol, exchange)
            
            historic_param = {
                "exchange": exchange,
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            
            data = self.smart_api.getCandleData(historic_param)
            
            if data.get('status') and data.get('data'):
                # Convert to DataFrame
                df = pd.DataFrame(data['data'], columns=[
                    "timestamp", "open", "high", "low", "close", "volume"
                ])
                
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp").reset_index(drop=True)
                
                # Convert to numeric
                for col in ["open", "high", "low", "close", "volume"]:
                    df[col] = pd.to_numeric(df[col])
                
                return df
            else:
                print(f"Failed to get historical data: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return None
    
    def get_symbol_token(self, symbol, exchange="NSE"):
        """Get symbol token for a given symbol - simplified version"""
        # This is a simplified mapping. In production, you'd use the searchScrip API
        symbol_mapping = {
            "NIFTY50": "99926000",
            "BANKNIFTY": "99926009",
            "RELIANCE": "2885",
            "TCS": "11536",
            "HDFCBANK": "1333",
            "INFY": "1594",
            "ICICIBANK": "4963",
            "HINDUNILVR": "356",
            "ITC": "424",
            "SBIN": "3045"
        }
        
        return symbol_mapping.get(symbol, "99926000")  # Default to NIFTY50
    
    def search_symbol(self, symbol):
        """Search for symbol token using searchScrip API"""
        try:
            if not self.is_connected or not self.smart_api:
                return None
            
            search_result = self.smart_api.searchScrip("NSE", symbol)
            
            if search_result.get('status') and search_result.get('data'):
                return search_result['data']
            else:
                return None
                
        except Exception as e:
            print(f"Error searching symbol: {e}")
            return None
    
    def get_live_price(self, symbol, exchange="NSE"):
        """Get live price for a symbol"""
        try:
            if not self.is_connected or not self.smart_api:
                return None
            
            symbol_token = self.get_symbol_token(symbol, exchange)
            
            ltp_data = {
                "exchange": exchange,
                "tradingsymbol": symbol,
                "symboltoken": symbol_token
            }
            
            response = self.smart_api.ltpData(exchange, symbol, symbol_token)
            
            if response.get('status') and response.get('data'):
                return float(response['data']['ltp'])
            else:
                print(f"Failed to get live price: {response.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error getting live price: {e}")
            return None
    
    def place_order(self, symbol, quantity, side, order_type="MARKET", price=0, exchange="NSE"):
        """Place an order"""
        try:
            if not self.is_connected or not self.smart_api:
                return None
            
            symbol_token = self.get_symbol_token(symbol, exchange)
            
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": symbol_token,
                "transactiontype": side.upper(),
                "exchange": exchange,
                "ordertype": order_type,
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": str(price) if order_type == "LIMIT" else "0",
                "squareoff": "0",
                "stoploss": "0",
                "quantity": str(quantity)
            }
            
            order_id = self.smart_api.placeOrder(order_params)
            
            if order_id:
                print(f"Order placed successfully. Order ID: {order_id}")
                return order_id
            else:
                print("Failed to place order")
                return None
                
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def get_portfolio(self):
        """Get current portfolio"""
        try:
            if not self.is_connected or not self.smart_api:
                return None
            
            holdings = self.smart_api.holding()
            positions = self.smart_api.position()
            
            portfolio_data = {
                "holdings": holdings.get('data', []) if holdings.get('status') else [],
                "positions": positions.get('data', []) if positions.get('status') else []
            }
            
            return portfolio_data
                
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return None
    
    def logout(self):
        """Logout from Angel One API"""
        try:
            if self.is_connected and self.smart_api and self.user_id:
                logout_response = self.smart_api.terminateSession(self.user_id)
                
                if logout_response.get('status'):
                    print("Successfully logged out from Angel One API")
                    self.access_token = None
                    self.refresh_token = None
                    self.feed_token = None
                    self.user_id = None
                    self.is_connected = False
                    return {"status": True, "message": "Logout successful"}
                else:
                    return {"status": False, "message": logout_response.get('message', 'Logout failed')}
            else:
                return {"status": False, "message": "Not logged in"}
                
        except Exception as e:
            print(f"Error during logout: {e}")
            return {"status": False, "message": f"Logout error: {str(e)}"}
    
    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        try:
            if not self.smart_api or not self.refresh_token:
                return {"status": False, "message": "No refresh token available"}
            
            token_response = self.smart_api.generateToken(self.refresh_token)
            
            if token_response.get('status'):
                self.access_token = token_response['data']['jwtToken']
                self.feed_token = token_response['data']['feedToken']
                return {"status": True, "message": "Token refreshed successfully"}
            else:
                return {"status": False, "message": token_response.get('message', 'Token refresh failed')}
                
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return {"status": False, "message": f"Token refresh error: {str(e)}"}
    
    def __del__(self):
        """Destructor to ensure logout"""
        if hasattr(self, 'is_connected') and self.is_connected:
            self.logout()