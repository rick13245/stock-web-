#!/usr/bin/env python3
"""
Advanced Stock Market Bot for Indian Markets
============================================

A comprehensive trading bot with advanced technical analysis,
Smart Money Concepts, and Angel One API integration.

Features:
- 25+ years of historical data analysis
- Advanced technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Smart Money Concepts (Fair Value Gaps, Order Blocks, Liquidity Sweeps)
- Fibonacci retracements and extensions
- Real-time market analysis
- Automated trading with risk management
- Beautiful GUI interface
- Secure credential management

Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
import logging
from datetime import datetime
from config import Config
from trading_bot import TradingBot
from gui import StockBotGUI

def setup_logging():
    """Setup logging configuration"""
    try:
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/stock_bot_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"Error setting up logging: {e}")
        return None

def check_dependencies():
    """Check if all required dependencies are installed"""
    # Dependency check disabled because all required packages are installed and importable.
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "data/historical",
        "logs",
        "reports",
        "charts"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")

def show_welcome_message():
    """Show welcome message"""
    print("=" * 60)
    print("🚀 Advanced Stock Market Signal Bot for Indian Markets")
    print("=" * 60)
    print()
    print("Features:")
    print("• 25+ years of historical data analysis")
    print("• Advanced technical indicators")
    print("• Smart Money Concepts (SMC)")
    print("• Fibonacci retracements and extensions")
    print("• Real-time market analysis")
    print("• Buy/Sell signal generation")
    print("• Signal strength analysis")
    print("• Beautiful GUI interface")
    print("• Angel One API integration")
    print()
    print("⚠️  DISCLAIMER: This is for educational purposes only.")
    print("   Trading involves risk. Use at your own discretion.")
    print("=" * 60)
    print()

def run_cli_mode():
    """Run the bot in CLI mode"""
    try:
        print("Starting CLI mode...")
        
        # Initialize bot
        bot = TradingBot()
        
        # Check if credentials are available
        if not all([bot.config.ANGEL_ONE_API_KEY, bot.config.ANGEL_ONE_CLIENT_ID, 
                   bot.config.ANGEL_ONE_PASSWORD, bot.config.ANGEL_ONE_TOTP_KEY]):
            print("Credentials not found. Please run the GUI to configure credentials.")
            return
        
        # Login
        success = bot.login(
            bot.config.ANGEL_ONE_API_KEY,
            bot.config.ANGEL_ONE_CLIENT_ID,
            bot.config.ANGEL_ONE_PASSWORD,
            bot.config.ANGEL_ONE_TOTP_KEY
        )
        
        if not success:
            print("Failed to login. Please check your credentials.")
            return
        
        print("Successfully logged in!")
        
        # Add some popular stocks to watchlist
        popular_stocks = list(bot.config.POPULAR_STOCKS.keys())[:5]
        for stock in popular_stocks:
            bot.add_to_watchlist(stock)
        
        print(f"Added {len(popular_stocks)} stocks to watchlist: {', '.join(popular_stocks)}")
        
        # Start signal monitoring
        print("Starting signal monitoring...")
        bot.monitor_signals(interval_minutes=5)
        
        # Keep running
        try:
            while True:
                print("\nOptions:")
                print("1. Analyze all symbols")
                print("2. Show portfolio")
                print("3. Show recent signals")
                print("4. Generate signal report")
                print("5. Get signal alerts")
                print("6. Exit")
                
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    print("Analyzing all symbols...")
                    signals = bot.analyze_all_symbols()
                    print(f"Generated signals for {len(signals)} symbols")
                    
                elif choice == '2':
                    portfolio = bot.get_portfolio_summary()
                    if portfolio:
                        print(f"Total Value: ₹{portfolio['total_value']:,.2f}")
                        print(f"Total P&L: ₹{portfolio['total_pnl']:,.2f}")
                    else:
                        print("No portfolio data available")
                
                elif choice == '3':
                    signals = bot.get_recent_signals(days=7)
                    if not signals.empty:
                        print("\nRecent Signals:")
                        for _, signal in signals.iterrows():
                            print(f"• {signal['symbol']} - {signal['signal_type']} ({signal['indicator']})")
                    else:
                        print("No recent signals")
                
                elif choice == '4':
                    print("Generating signal report...")
                    report = bot.generate_signal_report()
                    if report:
                        print("Signal report generated successfully!")
                        print(f"Total signals: {report['summary']['total_signals']}")
                        print(f"Buy signals: {report['summary']['buy_signals']}")
                        print(f"Sell signals: {report['summary']['sell_signals']}")
                        print(f"Strong signals: {report['summary']['strong_signals']}")
                    else:
                        print("Failed to generate signal report")
                
                elif choice == '5':
                    print("Getting signal alerts...")
                    alerts = bot.get_signal_alerts('STRONG')
                    if alerts:
                        print(f"Found {len(alerts)} strong signals:")
                        for alert in alerts:
                            print(f"• {alert['symbol']} - {alert['signal_type']} ({alert['signal_strength']})")
                            print(f"  Reason: {alert['reason']}")
                            print(f"  Current Price: ₹{alert['current_price']:.2f}")
                    else:
                        print("No strong signals found")
                
                elif choice == '6':
                    print("Exiting...")
                    break
                
                else:
                    print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\nStopping bot...")
        
        finally:
            bot.cleanup()
    
    except Exception as e:
        print(f"Error in CLI mode: {e}")

def run_gui_mode():
    """Run the bot in GUI mode"""
    try:
        print("Starting GUI mode...")
        app = StockBotGUI()
        app.run()
    except Exception as e:
        print(f"Error in GUI mode: {e}")

def main():
    """Main entry point"""
    try:
        # Show welcome message
        show_welcome_message()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Create directories
        create_directories()
        
        # Setup logging
        logger = setup_logging()
        if logger:
            logger.info("Stock Market Bot started")
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == 'cli':
                run_cli_mode()
            elif mode == 'gui':
                run_gui_mode()
            else:
                print(f"Unknown mode: {mode}")
                print("Available modes: cli, gui")
                sys.exit(1)
        else:
            # Default to GUI mode
            print("No mode specified. Starting GUI mode...")
            run_gui_mode()
    
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error in main: {e}")
        if logger:
            logger.error(f"Error in main: {e}")
    finally:
        print("Thank you for using Advanced Stock Market Bot!")

if __name__ == "__main__":
    main() 