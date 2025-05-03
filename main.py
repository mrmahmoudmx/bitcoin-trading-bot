import time
from datetime import datetime
import config
import logger
from binance_api import BinanceClient
from strategy import MovingAverageCrossoverStrategy
from risk_management import RiskManager
from database import Database

class TradingBot:
    def __init__(self):
        """Initialize the trading bot with all required components"""
        self.log = logger.get_logger()
        self.log.info("Initializing Trading Bot...")
        
        # Initialize components
        self.binance_client = BinanceClient()
        self.strategy = MovingAverageCrossoverStrategy()
        self.risk_manager = RiskManager()
        self.db = Database()
        
        # Bot state
        self.is_running = False
        self.current_position = None
        
        self.log.info("Trading Bot initialized successfully")

    def start(self):
        """Start the trading bot"""
        self.log.info("Starting Trading Bot...")
        self.is_running = True
        
        # Test API connection
        if not self.binance_client.check_api_connection():
            self.log.error("Failed to connect to Binance API. Stopping bot.")
            return

        try:
            while self.is_running:
                self.execute_trading_cycle()
                time.sleep(config.CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            self.log.info("Received keyboard interrupt. Stopping bot...")
            self.stop()
        except Exception as e:
            self.log.error(f"Unexpected error in main loop: {str(e)}")
            self.stop()

    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        self.log.info("Trading Bot stopped")

    def execute_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            # Get current market data
            current_price = self.binance_client.get_current_price()
            if not current_price:
                self.log.error("Failed to get current price")
                return

            # Get historical data for analysis
            historical_data = self.binance_client.get_historical_prices()
            if historical_data.empty:
                self.log.error("Failed to get historical data")
                return

            # Generate trading signal
            signal = self.strategy.generate_trade_signal(historical_data)
            self.log.info(f"Generated signal: {signal}")

            # If we have a trade signal (BUY or SELL)
            if signal in ['BUY', 'SELL']:
                self.execute_trade(signal, current_price)

            # Update performance metrics
            self.update_performance_metrics()

        except Exception as e:
            self.log.error(f"Error in trading cycle: {str(e)}")

    def execute_trade(self, signal, current_price):
        """Execute a trade based on the signal"""
        try:
            # Get account balance
            balance = self.binance_client.get_account_balance()
            
            # Validate trade with risk manager
            if not self.risk_manager.validate_trade(signal, current_price, balance):
                self.log.warning("Trade validation failed")
                return

            # Calculate position size
            quantity = self.risk_manager.calculate_position_size(balance, current_price)
            if quantity <= 0:
                self.log.warning("Invalid position size calculated")
                return

            # Execute order
            order = self.binance_client.place_order(
                config.TARGET_SYMBOL,
                signal,
                quantity
            )

            if order:
                # Calculate stop loss
                stop_loss = self.risk_manager.calculate_stop_loss(current_price, signal)
                
                # Record trade in database
                trade_data = {
                    'symbol': config.TARGET_SYMBOL,
                    'side': signal,
                    'quantity': quantity,
                    'price': current_price,
                    'status': order['status'],
                    'stop_loss': stop_loss
                }
                self.db.insert_trade(trade_data)
                
                # Update position tracking
                self.current_position = signal
                
                self.log.info(f"Successfully executed {signal} order: {quantity} {config.TARGET_SYMBOL} @ {current_price}")
            else:
                self.log.error("Failed to execute order")

        except Exception as e:
            self.log.error(f"Error executing trade: {str(e)}")

    def update_performance_metrics(self):
        """Update and store performance metrics"""
        try:
            # Get trade history
            trades_df = self.db.get_trade_history()
            if trades_df.empty:
                return

            # Calculate metrics
            total_trades = len(trades_df)
            winning_trades = len(trades_df[trades_df['pnl'] > 0])
            losing_trades = len(trades_df[trades_df['pnl'] < 0])
            
            if total_trades > 0:
                win_rate = winning_trades / total_trades
                total_pnl = trades_df['pnl'].sum()
                
                metrics = {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'total_profit_loss': total_pnl
                }
                
                # Store metrics
                self.db.insert_performance_metrics(metrics)
                self.log.info(f"Performance metrics updated: Win Rate = {win_rate:.2%}, Total PnL = {total_pnl:.8f}")

        except Exception as e:
            self.log.error(f"Error updating performance metrics: {str(e)}")

def main():
    """Main entry point for the trading bot"""
    bot = TradingBot()
    
    # Print startup message
    print("=" * 50)
    print("Bitcoin Trading Bot")
    print("=" * 50)
    print(f"Trading pair: {config.TARGET_SYMBOL}")
    print(f"Mode: {'Simulation' if config.SIMULATION_MODE else 'Live Trading'}")
    print("Press Ctrl+C to stop the bot")
    print("=" * 50)
    
    # Start the bot
    bot.start()

if __name__ == "__main__":
    main()
