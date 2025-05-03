# Bitcoin Trading Bot

A Python-based cryptocurrency trading bot that implements a Moving Average Crossover strategy for automated Bitcoin trading on the Binance exchange.

## Features

- Moving Average Crossover trading strategy
- Real-time market data analysis
- Risk management system
- Trade execution on Binance
- Performance tracking and metrics
- SQLite database for trade history
- Simulation mode for testing
- Comprehensive logging system

## Prerequisites

- Python 3.8 or higher
- Binance API key and secret
- Sufficient balance in your Binance account (for live trading)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bitcoin-trading-bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
export BINANCE_API_KEY='your_api_key'
export BINANCE_API_SECRET='your_api_secret'
```

## Configuration

Edit `config.py` to customize your trading parameters:

- `SIMULATION_MODE`: Set to `True` for testing (no real trades)
- `TARGET_SYMBOL`: Trading pair (default: BTCUSDT)
- `TRADE_AMOUNT`: Amount of BTC per trade
- `SHORT_WINDOW`: Short-term moving average period
- `LONG_WINDOW`: Long-term moving average period
- `MAX_TRADE_RISK`: Maximum risk per trade (as decimal)
- `STOP_LOSS_PCT`: Stop loss percentage (as decimal)

## Usage

1. Start the bot:
```bash
python main.py
```

2. Monitor the logs:
- Check `logs/bot_<timestamp>.log` for detailed operation logs
- Console output shows real-time trading activities

3. Stop the bot:
- Press `Ctrl+C` to gracefully stop the bot

## Trading Strategy

The bot uses a Moving Average Crossover strategy:

1. Calculates short-term (5 periods) and long-term (20 periods) moving averages
2. Generates BUY signal when short MA crosses above long MA
3. Generates SELL signal when short MA crosses below long MA
4. Validates signals using additional technical indicators
5. Implements risk management rules before executing trades

## Risk Management

The bot includes several risk management features:

- Position sizing based on account balance
- Stop-loss orders for each trade
- Maximum trade risk per position
- Daily loss limits
- Volatility checks
- Win rate tracking

## Database

Trade history and performance metrics are stored in SQLite:

- `trades` table: Records all executed trades
- `performance_metrics` table: Stores trading performance data

## Project Structure

```
bitcoin-trading-bot/
├── main.py              # Main bot execution
├── config.py            # Configuration settings
├── binance_api.py       # Binance API wrapper
├── strategy.py          # Trading strategy implementation
├── risk_management.py   # Risk management system
├── database.py          # Database operations
├── logger.py            # Logging configuration
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Warning

**Use this bot at your own risk. Cryptocurrency trading carries significant risks:**

- This bot is for educational purposes
- Never trade with money you can't afford to lose
- Always test in simulation mode first
- Past performance doesn't guarantee future results
- Verify all trading logic before live trading

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
