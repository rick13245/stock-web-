try:
    from flask import Flask, render_template, jsonify, request
except ImportError:
    print("Flask not found. Please install it with: pip install flask")
    exit(1)

import json
import os
from datetime import datetime

try:
    from trading_bot import TradingBot
    from config import Config
    TRADING_BOT_AVAILABLE = True
except ImportError as e:
    print(f"Trading bot modules not fully available: {e}")
    print("Some features may be limited.")
    TRADING_BOT_AVAILABLE = False

app = Flask(__name__)
bot = None
config = Config() if TRADING_BOT_AVAILABLE else None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get bot status"""
    global bot
    if bot is None:
        return jsonify({'status': 'Not connected', 'logged_in': False})
    
    return jsonify({
        'status': 'Connected' if bot.is_running else 'Stopped',
        'logged_in': bot.api.is_logged_in if hasattr(bot.api, 'is_logged_in') else False,
        'watchlist_count': len(bot.watchlist) if bot.watchlist else 0
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Login to the trading API"""
    global bot
    
    if not TRADING_BOT_AVAILABLE:
        return jsonify({'success': False, 'message': 'Trading bot modules not available'})
    
    try:
        bot = TradingBot()
        
        # For demo purposes, we'll use mock credentials or skip login
        # In a real implementation, you'd get these from the request
        success = True  # Mock successful login
        
        if success:
            return jsonify({'success': True, 'message': 'Login successful (demo mode)'})
        else:
            return jsonify({'success': False, 'message': 'Login failed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/watchlist')
def get_watchlist():
    """Get current watchlist"""
    global bot
    if bot is None:
        return jsonify({'watchlist': []})
    
    return jsonify({'watchlist': bot.watchlist})

@app.route('/api/add_symbol', methods=['POST'])
def add_symbol():
    """Add symbol to watchlist"""
    global bot
    if bot is None:
        return jsonify({'success': False, 'message': 'Bot not initialized'})
    
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if not symbol:
        return jsonify({'success': False, 'message': 'Symbol required'})
    
    success = bot.add_to_watchlist(symbol)
    return jsonify({'success': success, 'message': f'{"Added" if success else "Failed to add"} {symbol}'})

@app.route('/api/remove_symbol', methods=['POST'])
def remove_symbol():
    """Remove symbol from watchlist"""
    global bot
    if bot is None:
        return jsonify({'success': False, 'message': 'Bot not initialized'})
    
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if not symbol:
        return jsonify({'success': False, 'message': 'Symbol required'})
    
    success = bot.remove_from_watchlist(symbol)
    return jsonify({'success': success, 'message': f'{"Removed" if success else "Failed to remove"} {symbol}'})

@app.route('/api/analyze_symbol', methods=['POST'])
def analyze_symbol():
    """Analyze a specific symbol"""
    global bot
    if bot is None:
        return jsonify({'success': False, 'message': 'Bot not initialized'})
    
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if not symbol:
        return jsonify({'success': False, 'message': 'Symbol required'})
    
    try:
        signals = bot.analyze_symbol(symbol)
        return jsonify({'success': True, 'signals': signals})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/recent_signals')
def get_recent_signals():
    """Get recent signals"""
    global bot
    if bot is None:
        return jsonify({'signals': []})
    
    try:
        signals = bot.get_recent_signals(days=7)
        if not signals.empty:
            signals_list = signals.to_dict('records')
            return jsonify({'signals': signals_list})
        else:
            return jsonify({'signals': []})
    except Exception as e:
        return jsonify({'signals': [], 'error': str(e)})

@app.route('/api/portfolio')
def get_portfolio():
    """Get portfolio summary"""
    global bot
    if bot is None:
        return jsonify({'portfolio': None})
    
    try:
        portfolio = bot.get_portfolio_summary()
        return jsonify({'portfolio': portfolio})
    except Exception as e:
        return jsonify({'portfolio': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)