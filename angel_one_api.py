import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from config import Config

class AngelOneAPI:
    def __init__(self):
        self.base_url = "https://apiconnect.angelbroking.com"
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.is_connected = False
        self.local_ip = None
        self.public_ip = None
        self.mac_address = None
        
    def _get_headers_with_network_info(self):
        """Helper method to get headers with network identification"""
        headers = self.session.headers.copy()
        if self.local_ip:
            headers["X-ClientLocalIP"] = self.local_ip
        if self.public_ip:
            headers["X-ClientPublicIP"] = self.public_ip
        if self.mac_address:
            headers["X-MACAddress"] = self.mac_address
        return headers
        


    
    def get_historical_data(self, symbol, exchange="NSE", interval="1D", from_date=None, to_date=None):
        """Get historical data for a symbol"""
        try:
            if not self.is_connected:
                print("Not connected to Angel One API")
                return None
            
            if from_date is None:
                from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            if to_date is None:
                to_date = datetime.now().strftime("%Y-%m-%d")
            
            # Convert interval to Angel One format
            interval_map = {
                "1D": "1D",
                "1W": "1W",
                "1M": "1M",
                "1H": "1H",
                "15M": "15M",
                "5M": "5M",
                "1M": "1M"
            }
            
            angel_interval = interval_map.get(interval, "1D")
            
            payload = {
                "exchange": exchange,
                "symboltoken": self.get_symbol_token(symbol, exchange),
                "interval": angel_interval,
                "fromdate": from_date,
                "todate": to_date
            }
            
            # Get headers with network identification
            headers = self._get_headers_with_network_info()
            
            response = self.session.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/getCandleData",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    candles = data["data"]
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(candles, columns=[
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
            else:
                print(f"Historical data request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return None
    
    def get_symbol_token(self, symbol, exchange="NSE"):
        """Get symbol token for a given symbol"""
        try:
            # This is a simplified version. In production, you'd need to maintain a mapping
            # or use Angel One's symbol search API
            symbol_mapping = {
                "NIFTY50": "26009",
                "BANKNIFTY": "26017",
                "RELIANCE": "2885",
                "TCS": "11536",
                "HDFCBANK": "341",
                "INFY": "1594",
                "ICICIBANK": "4963",
                "HINDUNILVR": "3045",
                "ITC": "4244",
                "SBIN": "3045"
            }
            
            return symbol_mapping.get(symbol, "26009")  # Default to NIFTY50
            
        except Exception as e:
            print(f"Error getting symbol token: {e}")
            return None
    
    def get_live_price(self, symbol, exchange="NSE"):
        """Get live price for a symbol"""
        try:
            if not self.is_connected:
                print("Not connected to Angel One API")
                return None
            
            symbol_token = self.get_symbol_token(symbol, exchange)
            
            payload = {
                "exchange": exchange,
                "tradingsymbol": symbol,
                "symboltoken": symbol_token
            }
            
            # Get headers with network identification
            headers = self._get_headers_with_network_info()
            
            response = self.session.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/getLtpData",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    ltp_data = data["data"]["ltp"]
                    return float(ltp_data)
                else:
                    print(f"Failed to get live price: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Live price request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting live price: {e}")
            return None
    
    def place_order(self, symbol, quantity, side, order_type="MARKET", price=0, exchange="NSE"):
        """Place an order"""
        try:
            if not self.is_connected:
                print("Not connected to Angel One API")
                return None
            
            symbol_token = self.get_symbol_token(symbol, exchange)
            
            payload = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": symbol_token,
                "transactiontype": side.upper(),
                "exchange": exchange,
                "ordertype": order_type,
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": str(price),
                "squareoff": "0",
                "stoploss": "0",
                "quantity": str(quantity)
            }
            
            # Get headers with network identification
            headers = self._get_headers_with_network_info()
            
            response = self.session.post(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    order_id = data["data"]["orderid"]
                    print(f"Order placed successfully. Order ID: {order_id}")
                    return order_id
                else:
                    print(f"Failed to place order: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Place order request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def get_portfolio(self):
        """Get current portfolio"""
        try:
            if not self.is_connected:
                print("Not connected to Angel One API")
                return None
            
            # Get headers with network identification
            headers = self._get_headers_with_network_info()
            
            response = self.session.get(
                f"{self.base_url}/rest/secure/angelbroking/order/v1/getPosition",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["status"]:
                    return data["data"]
                else:
                    print(f"Failed to get portfolio: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"Portfolio request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return None
    
    def logout(self):
        """Logout from Angel One API"""
        try:
            if self.is_connected:
                # Get headers with network identification
                headers = self._get_headers_with_network_info()
                
                response = self.session.post(
                    f"{self.base_url}/rest/secure/angelbroking/user/v1/logout",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("Successfully logged out from Angel One API")
                
                self.access_token = None
                self.refresh_token = None
                self.user_id = None
                self.is_connected = False
                
        except Exception as e:
            print(f"Error during logout: {e}")
    
    def __del__(self):
        """Destructor to ensure logout"""
        self.logout()