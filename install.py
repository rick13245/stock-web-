#!/usr/bin/env python3
"""
Installation Script for Advanced Stock Market Bot
================================================

This script helps users install and configure the stock market bot.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("=" * 60)
    print("🚀 Advanced Stock Market Bot - Installation")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        "data",
        "data/historical",
        "logs",
        "reports",
        "charts"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")
            return False
    
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("\nTesting imports...")
    
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
        'dash', 'ta', 'yfinance', 'requests', 'python_dotenv',
        'schedule', 'psutil', 'cryptography', 'keyring', 'PIL',
        'sklearn', 'scipy', 'pyotp'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully!")
    return True

def check_angel_one_setup():
    """Check Angel One API setup"""
    print("\nAngel One API Setup:")
    print("To use this bot, you need an Angel One trading account.")
    print("Follow these steps:")
    print("1. Visit https://www.angelone.in/")
    print("2. Sign up for a trading account")
    print("3. Complete KYC verification")
    print("4. Generate API credentials")
    print("5. Note down your API Key, Client ID, Password, and TOTP Key")
    print()
    print("⚠️  IMPORTANT: Keep your credentials secure and never share them!")

def show_next_steps():
    """Show next steps after installation"""
    print("\n" + "=" * 60)
    print("🎉 Installation Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Run the bot: python main.py")
    print("2. Login with your Angel One credentials")
    print("3. Add stocks to your watchlist")
    print("4. Configure risk management settings")
    print("5. Start automated trading")
    print()
    print("Documentation: README.md")
    print("Support: Check the README for troubleshooting")
    print()
    print("⚠️  DISCLAIMER: This is for educational purposes only.")
    print("   Trading involves risk. Use at your own discretion.")

def main():
    """Main installation function"""
    try:
        print_banner()
        
        # Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Install dependencies
        if not install_dependencies():
            sys.exit(1)
        
        # Create directories
        if not create_directories():
            sys.exit(1)
        
        # Test imports
        if not test_imports():
            print("\n❌ Some packages failed to import.")
            print("Try running: pip install -r requirements.txt")
            sys.exit(1)
        
        # Check Angel One setup
        check_angel_one_setup()
        
        # Show next steps
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 