"""
Configuration file for NYSE Investment Opportunity Detection Agent.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# List of 20 NYSE tickers to monitor
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "VIST", "META",
    "NVDA", "TSLA", "JPM", "V", "MU",
    "WMT", "NU", "CRWV", "ONDS", "GGAL",
    "NFLX", "CEPU", "EDN", "BMA", "LOMA"
]

# SMA Configuration
SMA_PERIOD = 29  # 29-day Simple Moving Average

# Dispersion threshold for alerts (percentage)
DISPERSION_THRESHOLD = 15.0  # Alert when dispersion > 20% or < -20%

# Data download settings
LOOKBACK_DAYS = 60  # Days of historical data to download

# Email Configuration (loaded from environment variables)
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "sender_email": os.getenv("EMAIL_SENDER", ""),
    "sender_password": os.getenv("EMAIL_PASSWORD", ""),
    "recipient_email": os.getenv("EMAIL_RECIPIENT", ""),
}

# Logging configuration
LOG_FILE = "dispersion_scanner.log"
