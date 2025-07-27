import pandas as pd
import numpy as np
import sqlite3
import os
import json
from datetime import datetime, timedelta
import yfinance as yf
from config import Config

class DataManager:
    def __init__(self):
        self.config = Config()
        self.db_path = self.config.DATABASE_PATH
        self.historical_path = self.config.HISTORICAL_DATA_PATH
        self.init_database()
        self.init_directories()
    
    def init_directories(self):
        """Initialize necessary directories"""
        try:
            os.makedirs("data", exist_ok=True)
            os.makedirs(self.historical_path, exist_ok=True)
            os.makedirs("logs", exist_ok=True)
            os.makedirs("reports", exist_ok=True)
        except Exception as e:
            print(f"Error creating directories: {e}")
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    indicator TEXT NOT NULL,
                    strength TEXT NOT NULL,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    executed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    quantity INTEGER,
                    avg_price REAL,
                    current_price REAL,
                    pnl REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity INTEGER,
                    price REAL,
                    order_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'PENDING'
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def save_stock_data(self, symbol, df):
        """Save stock data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Prepare data for insertion
            df_to_save = df.copy()
            df_to_save['symbol'] = symbol
            df_to_save = df_to_save[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            # Save to database
            df_to_save.to_sql('stock_data', conn, if_exists='append', index=False)
            
            # Also save as CSV for backup
            csv_path = os.path.join(self.historical_path, f"{symbol}_data.csv")
            df_to_save.to_csv(csv_path, index=False)
            
            conn.close()
            print(f"Data saved for {symbol}")
            
        except Exception as e:
            print(f"Error saving stock data: {e}")
    
    def get_stock_data(self, symbol, start_date=None, end_date=None, limit=None):
        """Get stock data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f"SELECT * FROM stock_data WHERE symbol = '{symbol}'"
            
            if start_date:
                query += f" AND timestamp >= '{start_date}'"
            if end_date:
                query += f" AND timestamp <= '{end_date}'"
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error getting stock data: {e}")
            return pd.DataFrame()
    
    def get_latest_data(self, symbol, days=30):
        """Get latest stock data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            return self.get_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            
        except Exception as e:
            print(f"Error getting latest data: {e}")
            return pd.DataFrame()
    
    def download_historical_data(self, symbol, years=25):
        """Download historical data using yfinance"""
        try:
            print(f"Downloading {years} years of historical data for {symbol}...")
            
            # Add .NS suffix for Indian stocks
            if not symbol.endswith('.NS'):
                symbol_with_suffix = f"{symbol}.NS"
            else:
                symbol_with_suffix = symbol
            
            # Download data
            ticker = yf.Ticker(symbol_with_suffix)
            df = ticker.history(period=f"{years}y")
            
            if df.empty:
                print(f"No data found for {symbol}")
                return None
            
            # Reset index to make date a column
            df = df.reset_index()
            
            # Rename columns to match our format
            df = df.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Save to database
            self.save_stock_data(symbol, df)
            
            print(f"Successfully downloaded {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            print(f"Error downloading historical data for {symbol}: {e}")
            return None
    
    def update_latest_data(self, symbol):
        """Update latest data for a symbol"""
        try:
            # Get the last date in our database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT MAX(timestamp) FROM stock_data 
                WHERE symbol = '{symbol}'
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result[0]:
                last_date = pd.to_datetime(result[0])
                start_date = last_date + timedelta(days=1)
            else:
                # No data exists, download full history
                return self.download_historical_data(symbol)
            
            # Download only new data
            if start_date.date() < datetime.now().date():
                print(f"Updating data for {symbol} from {start_date.date()}")
                
                if not symbol.endswith('.NS'):
                    symbol_with_suffix = f"{symbol}.NS"
                else:
                    symbol_with_suffix = symbol
                
                ticker = yf.Ticker(symbol_with_suffix)
                df = ticker.history(start=start_date)
                
                if not df.empty:
                    df = df.reset_index()
                    df = df.rename(columns={
                        'Date': 'timestamp',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })
                    
                    self.save_stock_data(symbol, df)
                    print(f"Updated {len(df)} new records for {symbol}")
                    return df
                else:
                    print(f"No new data available for {symbol}")
                    return None
            else:
                print(f"Data for {symbol} is already up to date")
                return None
                
        except Exception as e:
            print(f"Error updating latest data for {symbol}: {e}")
            return None
    
    def save_signal(self, symbol, signal_type, indicator, strength, reason):
        """Save trading signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO signals (symbol, signal_type, indicator, strength, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, signal_type, indicator, strength, reason))
            
            conn.commit()
            conn.close()
            
            print(f"Signal saved: {signal_type} for {symbol}")
            
        except Exception as e:
            print(f"Error saving signal: {e}")
    
    def get_recent_signals(self, symbol=None, days=7):
        """Get recent trading signals"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f"""
                SELECT * FROM signals 
                WHERE timestamp >= datetime('now', '-{days} days')
            """
            
            if symbol:
                query += f" AND symbol = '{symbol}'"
            
            query += " ORDER BY timestamp DESC"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"Error getting recent signals: {e}")
            return pd.DataFrame()
    
    def save_trade(self, symbol, side, quantity, price, order_id=None):
        """Save trade to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (symbol, side, quantity, price, order_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, side, quantity, price, order_id))
            
            conn.commit()
            conn.close()
            
            print(f"Trade saved: {side} {quantity} {symbol} @ {price}")
            
        except Exception as e:
            print(f"Error saving trade: {e}")
    
    def get_trade_history(self, symbol=None, days=30):
        """Get trade history"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f"""
                SELECT * FROM trades 
                WHERE timestamp >= datetime('now', '-{days} days')
            """
            
            if symbol:
                query += f" AND symbol = '{symbol}'"
            
            query += " ORDER BY timestamp DESC"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"Error getting trade history: {e}")
            return pd.DataFrame()
    
    def update_portfolio(self, symbol, quantity, avg_price, current_price):
        """Update portfolio data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate P&L
            pnl = (current_price - avg_price) * quantity
            
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio (symbol, quantity, avg_price, current_price, pnl)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, quantity, avg_price, current_price, pnl))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating portfolio: {e}")
    
    def get_portfolio(self):
        """Get current portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM portfolio", conn)
            conn.close()
            return df
            
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return pd.DataFrame()
    
    def cleanup_old_data(self, days_to_keep=365):
        """Clean up old data to save space"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old stock data
            cursor.execute(f"""
                DELETE FROM stock_data 
                WHERE timestamp < datetime('now', '-{days_to_keep} days')
            """)
            
            # Delete old signals
            cursor.execute(f"""
                DELETE FROM signals 
                WHERE timestamp < datetime('now', '-{days_to_keep} days')
            """)
            
            # Delete old trades
            cursor.execute(f"""
                DELETE FROM trades 
                WHERE timestamp < datetime('now', '-{days_to_keep} days')
            """)
            
            conn.commit()
            conn.close()
            
            print(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
    
    def export_data(self, symbol, format='csv'):
        """Export data for a symbol"""
        try:
            df = self.get_stock_data(symbol)
            
            if df.empty:
                print(f"No data found for {symbol}")
                return None
            
            if format.lower() == 'csv':
                filename = f"reports/{symbol}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
            elif format.lower() == 'json':
                filename = f"reports/{symbol}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                df.to_json(filename, orient='records', date_format='iso')
            else:
                print(f"Unsupported format: {format}")
                return None
            
            print(f"Data exported to {filename}")
            return filename
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None 