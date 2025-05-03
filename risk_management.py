import numpy as np
import config
import logger

class RiskManager:
    def __init__(self):
        """Initialize risk management parameters"""
        self.log = logger.get_logger()
        self.max_trade_risk = config.MAX_TRADE_RISK
        self.stop_loss_pct = config.STOP_LOSS_PCT
        self.position_history = []

    def calculate_position_size(self, balance, current_price):
        """
        Calculate the appropriate position size based on account balance and risk parameters
        Returns: Quantity to trade
        """
        try:
            if config.SIMULATION_MODE:
                # In simulation mode, use a fixed percentage of the balance
                trade_amount = balance * 0.1  # Use 10% of balance per trade
                position_size = trade_amount / current_price
            else:
                # Calculate maximum position size based on risk percentage
                max_risk_amount = balance * self.max_trade_risk
                position_size = max_risk_amount / current_price
            
            # Round to appropriate decimal places (Binance requires specific precision)
            position_size = round(position_size, 6)  # Adjust precision as needed
            
            # Ensure minimum trade size
            min_trade_size = 0.001  # Minimum trade size in BTC
            if position_size < min_trade_size:
                position_size = min_trade_size
            
            self.log.info(f"Calculated position size: {position_size} BTC")
            return position_size
            
        except Exception as e:
            self.log.error(f"Error calculating position size: {str(e)}")
            return 0.0

    def calculate_stop_loss(self, entry_price, side):
        """
        Calculate stop loss price based on entry price and trading direction
        Returns: Stop loss price
        """
        try:
            if side == 'BUY':
                stop_loss = entry_price * (1 - self.stop_loss_pct)
            else:  # SELL
                stop_loss = entry_price * (1 + self.stop_loss_pct)
            
            self.log.info(f"Stop loss calculated at: {stop_loss}")
            return stop_loss
            
        except Exception as e:
            self.log.error(f"Error calculating stop loss: {str(e)}")
            return None

    def validate_trade(self, signal, current_price, balance):
        """
        Validate if a trade should be executed based on various risk factors
        Returns: (bool) Whether the trade should proceed
        """
        try:
            position_size = self.calculate_position_size(balance, current_price)
            
            if config.SIMULATION_MODE:
                # In simulation mode, only check if we have any balance
                if balance <= 0:
                    self.log.warning("Trade rejected: Insufficient balance")
                    return False
            else:
                # In live mode, check minimum trade amount
                min_trade_amount = 0.001  # Minimum trade amount in BTC
                if position_size < min_trade_amount:
                    self.log.warning(f"Trade rejected: Position size {position_size} below minimum {min_trade_amount}")
                    return False

            # Check if we're within daily loss limit
            if self.check_daily_loss_limit():
                self.log.warning("Trade rejected: Daily loss limit reached")
                return False

            # Check market volatility
            if self.is_volatility_too_high(current_price):
                self.log.warning("Trade rejected: Market volatility too high")
                return False

            self.log.info(f"Trade validation passed - Position size: {position_size} BTC")
            return True

        except Exception as e:
            self.log.error(f"Error validating trade: {str(e)}")
            return False

    def check_daily_loss_limit(self):
        """
        Check if daily loss limit has been reached
        Returns: True if limit reached, False otherwise
        """
        try:
            # Get today's trades
            today_trades = [t for t in self.position_history if t['timestamp'].date() == datetime.now().date()]
            
            if not today_trades:
                return False
                
            # Calculate daily PnL
            daily_pnl = sum(t['pnl'] for t in today_trades)
            daily_loss_limit = -0.05  # 5% maximum daily loss
            
            return daily_pnl < daily_loss_limit
            
        except Exception as e:
            self.log.error(f"Error checking daily loss limit: {str(e)}")
            return True  # Err on the side of caution

    def is_volatility_too_high(self, current_price, historical_prices=None):
        """
        Check if market volatility is too high for safe trading
        Returns: True if volatility is too high, False otherwise
        """
        try:
            if historical_prices is None or len(historical_prices) < 20:
                return False
                
            # Calculate recent volatility
            returns = np.diff(historical_prices) / historical_prices[:-1]
            volatility = np.std(returns)
            
            # Define maximum acceptable volatility (e.g., 5%)
            max_volatility = 0.05
            
            return volatility > max_volatility
            
        except Exception as e:
            self.log.error(f"Error checking volatility: {str(e)}")
            return True  # Err on the side of caution

    def update_position_history(self, trade_info):
        """
        Update the history of positions and their performance
        """
        try:
            self.position_history.append(trade_info)
            self.log.info(f"Position history updated. Total positions: {len(self.position_history)}")
            
            # Maintain only recent history (e.g., last 100 trades)
            if len(self.position_history) > 100:
                self.position_history = self.position_history[-100:]
                
        except Exception as e:
            self.log.error(f"Error updating position history: {str(e)}")

    def get_risk_metrics(self):
        """
        Calculate and return various risk metrics
        Returns: Dictionary of risk metrics
        """
        try:
            if not self.position_history:
                return {
                    'win_rate': 0,
                    'average_profit': 0,
                    'max_drawdown': 0,
                    'sharpe_ratio': 0
                }

            # Calculate metrics
            profits = [t['pnl'] for t in self.position_history]
            winning_trades = len([p for p in profits if p > 0])
            
            metrics = {
                'win_rate': winning_trades / len(profits),
                'average_profit': np.mean(profits),
                'max_drawdown': self.calculate_max_drawdown(profits),
                'sharpe_ratio': self.calculate_sharpe_ratio(profits)
            }
            
            self.log.info(f"Risk metrics calculated: {metrics}")
            return metrics
            
        except Exception as e:
            self.log.error(f"Error calculating risk metrics: {str(e)}")
            return None

    @staticmethod
    def calculate_max_drawdown(profits):
        """Calculate maximum drawdown from a list of profits"""
        cumulative = np.cumsum(profits)
        max_drawdown = 0
        peak = cumulative[0]
        
        for value in cumulative:
            if value > peak:
                peak = value
            drawdown = peak - value
            max_drawdown = max(max_drawdown, drawdown)
            
        return max_drawdown

    @staticmethod
    def calculate_sharpe_ratio(profits, risk_free_rate=0.02):
        """Calculate Sharpe ratio from a list of profits"""
        if len(profits) < 2:
            return 0
            
        returns = np.array(profits)
        excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return 0
            
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)  # Annualized
