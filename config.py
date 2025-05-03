import os

# Binance API credentials
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Trading configuration
TARGET_SYMBOL = "BTCUSDT"
TRADE_AMOUNT = 0.001  # Trade 0.001 BTC per signal
SIMULATION_MODE = True  # Set to False for live trading

# Strategy parameters
SHORT_WINDOW = 5  # 5-period moving average
LONG_WINDOW = 20  # 20-period moving average

# Risk management
MAX_TRADE_RISK = 0.02  # Maximum 2% risk per trade
STOP_LOSS_PCT = 0.02  # 2% stop loss

# Intervals
CHECK_INTERVAL = 60  # Check for signals every 60 seconds

# Database
DB_FILENAME = "trade_history.db"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"
