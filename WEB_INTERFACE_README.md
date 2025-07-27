# Trading Bot Web Interface

## 🚀 Quick Start

Your trading bot now has a web interface! Here's how to access it:

### Option 1: Using the Startup Script (Recommended)

```bash
# Activate virtual environment (if you have one)
source venv/bin/activate

# Run the startup script
python start_web.py
```

### Option 2: Direct Flask Run

```bash
# Activate virtual environment
source venv/bin/activate

# Install Flask if not installed
pip install flask

# Run the web application
python web_app.py
```

### Option 3: Original CLI/GUI Mode

```bash
# Activate virtual environment
source venv/bin/activate

# CLI mode (text-based interface)
python main.py cli

# GUI mode (requires display)
python main.py gui
```

## 🌐 Accessing the Web Interface

Once the web server is running, you can access the trading bot dashboard at:

**http://localhost:8000**

## 📱 Features Available in Web Interface

- **📊 Real-time Bot Status** - See if the bot is connected and running
- **📈 Watchlist Management** - Add/remove stocks to monitor
- **🔍 Stock Analysis** - Analyze individual stocks for trading signals
- **📉 Recent Signals** - View recent buy/sell signals
- **💼 Portfolio Overview** - Check your portfolio value and P&L
- **⚡ Quick Actions** - Perform common tasks with one click

## 🔧 Troubleshooting

### Port 8000 Already in Use
If you get an error that port 8000 is already in use, try:
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Missing Dependencies
If you get import errors, install the missing packages:
```bash
pip install flask pandas numpy matplotlib seaborn plotly dash
```

### Virtual Environment Issues
If you're not in a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install flask
```

## 🔒 Security Note

This web interface is designed for local development and testing. For production use:
- Add proper authentication
- Use HTTPS
- Configure firewall rules
- Set up proper logging

## 🎯 What's Different from CLI/GUI?

| Feature | CLI | GUI | Web |
|---------|-----|-----|-----|
| User Interface | Text-based menu | Desktop window | Web browser |
| Accessibility | Terminal required | Display required | Any device with browser |
| Real-time Updates | Manual refresh | GUI updates | Auto-refresh via AJAX |
| Remote Access | SSH only | Local only | Network accessible |
| Platform Support | All platforms | Platform-specific | Universal |

## 📞 Need Help?

If you're still having trouble accessing the web interface:

1. **Check if the server is running**: Look for "Running on http://0.0.0.0:8000" message
2. **Try different browsers**: Chrome, Firefox, Safari, Edge
3. **Check firewall**: Ensure port 8000 is not blocked
4. **Use IP address**: Try http://127.0.0.1:8000 instead of localhost
5. **Check logs**: Look at the console output for error messages

The web interface provides the same functionality as the CLI/GUI versions but in a modern, accessible format that you can use from any web browser!