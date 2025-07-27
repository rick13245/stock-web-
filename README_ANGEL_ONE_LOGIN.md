# Angel One Stock Market Signal Bot - Login Implementation

## Overview

This project implements a comprehensive FastAPI-based stock market signal bot with **Angel One SmartAPI integration** for authentication and trading. The application provides buy/sell signals through advanced technical analysis and Smart Money Concepts.

## Features

✅ **Angel One Authentication**: Proper login implementation using Angel One SmartAPI  
✅ **FastAPI Web Application**: RESTful API with interactive documentation  
✅ **Beautiful Web Interface**: HTML frontend for easy login and testing  
✅ **Real-time Market Data**: Live price feeds and historical data  
✅ **Advanced Signal Generation**: Technical indicators and Smart Money Concepts  
✅ **Portfolio Management**: Track holdings and positions  
✅ **Trading Operations**: Place orders through Angel One API  

## Prerequisites

### Angel One Account Setup

1. **Open Angel One Demat Account**: Visit [Angel One](https://angelone.in/)
2. **Enable API Access**: Contact Angel One support to enable API access
3. **Get API Credentials**:
   - API Key
   - Client ID (Your Angel One Client ID)
   - Password (Your login password)
   - TOTP Secret Key (For 2FA authentication)

### TOTP Secret Key Setup

1. Enable 2FA in your Angel One account
2. When setting up authenticator app, save the **secret key** (QR code text)
3. This secret key is used to generate TOTP codes programmatically

## Installation & Setup

### 1. Clone and Install Dependencies

```bash
# Navigate to project directory
cd /workspace

# Install required packages
pip install --break-system-packages fastapi uvicorn pandas requests pyotp websocket-client logzero
```

### 2. Start the Server

```bash
# Make startup script executable
chmod +x start_server.sh

# Start the FastAPI server
./start_server.sh
```

The server will start on `http://localhost:8000`

### 3. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Using the Angel One Login

### Web Interface Method

1. **Open Browser**: Navigate to http://localhost:8000
2. **Enter Credentials**:
   - API Key: Your Angel One API key
   - Client ID: Your Angel One client ID
   - Password: Your Angel One password
   - TOTP Secret: Your 2FA secret key
3. **Click Login**: The system will generate TOTP and authenticate
4. **Access Dashboard**: After successful login, access trading features

### API Method

#### Login Endpoint

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "api_key": "your_api_key",
       "client_id": "your_client_id", 
       "password": "your_password",
       "totp_secret": "your_totp_secret"
     }'
```

#### Response

```json
{
  "status": true,
  "message": "Login successful",
  "data": {
    "user_id": "CLIENT123",
    "client_name": "Your Name",
    "email": "your@email.com",
    "mobile": "9876543210"
  },
  "access_token": "CLIENT123_1234567890.123"
}
```

#### Using the Access Token

Include the access token in subsequent API calls:

```bash
curl -X GET "http://localhost:8000/auth/profile" \
     -H "Authorization: Bearer CLIENT123_1234567890.123"
```

## Available API Endpoints

### Authentication
- `POST /auth/login` - Login with Angel One credentials
- `POST /auth/logout` - Logout and cleanup session
- `GET /auth/profile` - Get user profile information

### Market Data
- `POST /market/live-price` - Get real-time stock prices
- `POST /market/historical-data` - Fetch historical price data
- `POST /market/search-symbol` - Search for stock symbols

### Trading
- `POST /trading/place-order` - Place buy/sell orders
- `GET /trading/portfolio` - Get current portfolio

### Signal Analysis
- `POST /signals/analyze` - Analyze symbol and generate signals
- `GET /signals/all` - Get all recent signals
- `GET /signals/strong` - Get strong trading signals

### Watchlist
- `POST /watchlist/add` - Add symbols to watchlist
- `GET /watchlist` - Get current watchlist

### Configuration
- `GET /config/popular-stocks` - Get popular Indian stocks
- `GET /config/market-status` - Check market status

## Example Usage

### 1. Login and Get Live Price

```python
import requests

# Login
login_data = {
    "api_key": "your_api_key",
    "client_id": "your_client_id",
    "password": "your_password", 
    "totp_secret": "your_totp_secret"
}

response = requests.post("http://localhost:8000/auth/login", json=login_data)
token = response.json()["access_token"]

# Get live price
headers = {"Authorization": f"Bearer {token}"}
price_data = {"symbol": "RELIANCE", "exchange": "NSE"}

price_response = requests.post(
    "http://localhost:8000/market/live-price", 
    json=price_data, 
    headers=headers
)

print(price_response.json())
```

### 2. Generate Trading Signals

```python
# Analyze a symbol for signals
signal_data = {"symbol": "TCS", "timeframe": "1D"}

signal_response = requests.post(
    "http://localhost:8000/signals/analyze",
    json=signal_data,
    headers=headers
)

print(signal_response.json())
```

### 3. Place an Order

```python
# Place a buy order
order_data = {
    "symbol": "INFY",
    "quantity": 1,
    "side": "BUY",
    "order_type": "MARKET",
    "exchange": "NSE"
}

order_response = requests.post(
    "http://localhost:8000/trading/place-order",
    json=order_data,
    headers=headers
)

print(order_response.json())
```

## Security Notes

⚠️ **Important Security Considerations**:

1. **Never commit credentials** to version control
2. **Use environment variables** for production deployment
3. **Implement proper JWT tokens** for production (current implementation is simplified)
4. **Use HTTPS** in production environments
5. **Validate and sanitize** all user inputs
6. **Implement rate limiting** for API endpoints

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Login Failed**: Verify API credentials and TOTP secret
3. **Connection Error**: Check if Angel One API is accessible
4. **Server Not Starting**: Check if port 8000 is available

### Debug Mode

To run in debug mode with more detailed logs:

```bash
export PYTHONPATH=/workspace
python3 -c "
import uvicorn
uvicorn.run('fastapi_app:app', host='0.0.0.0', port=8000, reload=True, log_level='debug')
"
```

### Logs

Check server logs for debugging:
- Application logs are printed to console
- API request/response details available in debug mode

## Project Structure

```
/workspace/
├── fastapi_app.py          # Main FastAPI application
├── angel_one_api.py        # Angel One API integration
├── trading_bot.py          # Trading bot with signals
├── config.py              # Configuration settings
├── static/index.html      # Web interface
├── start_server.sh        # Server startup script
├── smartapi-python/       # Angel One SmartAPI library
└── requirements.txt       # Python dependencies
```

## Architecture

```mermaid
graph TB
    A[Web Browser] --> B[FastAPI Server]
    B --> C[Angel One API]
    B --> D[Trading Bot]
    B --> E[Signal Analysis]
    C --> F[Market Data]
    C --> G[Order Management]
    D --> H[Technical Indicators]
    E --> I[Smart Money Concepts]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## Disclaimer

⚠️ **This software is for educational purposes only. Trading involves significant risk and you should carefully consider your investment objectives, level of experience, and risk appetite. Past performance is not indicative of future results.**

## Support

For issues and questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review Angel One API documentation
3. Verify your credentials and network connectivity

---

**Happy Trading! 📈**