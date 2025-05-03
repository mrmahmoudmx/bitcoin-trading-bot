import logging
import config
import os
from datetime import datetime

def get_logger():
    """
    Configure and return a logger instance that writes to both console and file
    with proper formatting and log level from config.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create a logger instance
    logger = logging.getLogger('TradingBot')
    
    # Only add handlers if the logger doesn't have any
    if not logger.handlers:
        # Set log level from config
        level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)

        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler - create new log file for each run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_handler = logging.FileHandler(
            f'logs/bot_{timestamp}.log'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info('Logger initialized')

    return logger

# Create a global logger instance
logger = get_logger()

def log_trade(symbol, side, quantity, price, status):
    """
    Specialized logging function for trade events
    """
    message = f"TRADE: {side} {quantity} {symbol} @ {price} - Status: {status}"
    logger.info(message)

def log_signal(symbol, signal, price):
    """
    Specialized logging function for trading signals
    """
    message = f"SIGNAL: {signal} signal for {symbol} @ {price}"
    logger.info(message)

def log_error(error_msg, exc_info=None):
    """
    Specialized logging function for errors
    """
    logger.error(error_msg, exc_info=exc_info)

def log_balance(balance):
    """
    Specialized logging function for balance updates
    """
    logger.info(f"Current Balance: {balance}")
