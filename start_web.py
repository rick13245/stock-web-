#!/usr/bin/env python3
"""
Startup script for the Trading Bot Web Interface
This script will install Flask if needed and start the web application
"""

import subprocess
import sys
import os

def install_flask():
    """Install Flask if not available"""
    try:
        import flask
        print("✓ Flask is already installed")
        return True
    except ImportError:
        print("Installing Flask...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
            print("✓ Flask installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install Flask: {e}")
            return False

def start_web_app():
    """Start the web application"""
    try:
        # Import and run the Flask app
        from web_app import app
        print("🚀 Starting Trading Bot Web Interface...")
        print("📱 Access the dashboard at: http://localhost:8000")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=8000, debug=False)
        
    except ImportError as e:
        print(f"✗ Failed to import web_app: {e}")
        print("Make sure web_app.py exists and all dependencies are installed")
        return False
    except Exception as e:
        print(f"✗ Error starting web application: {e}")
        return False

def main():
    """Main entry point"""
    print("🤖 Trading Bot Web Interface Startup")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment detected")
    else:
        print("⚠️  Not in a virtual environment")
    
    # Install Flask if needed
    if not install_flask():
        print("✗ Cannot start without Flask. Please install it manually:")
        print("   pip install flask")
        sys.exit(1)
    
    # Start the web application
    start_web_app()

if __name__ == "__main__":
    main()