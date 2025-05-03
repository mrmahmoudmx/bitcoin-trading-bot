import pandas as pd
import numpy as np
import config
import logger

class MovingAverageCrossoverStrategy:
    def __init__(self):
        """Initialize strategy with configuration parameters"""
        self.log = logger.get_logger()
        self.short_window = config.SHORT_WINDOW
        self.long_window = config.LONG_WINDOW
        self.current_position = None  # Can be 'LONG' or 'SHORT' or None

    def calculate_moving_averages(self, df):
        """
        Calculate short and long moving averages
        Returns DataFrame with additional columns for moving averages
        """
        try:
            # Calculate moving averages
            df['SMA_short'] = df['close'].rolling(window=self.short_window).mean()
            df['SMA_long'] = df['close'].rolling(window=self.long_window).mean()
            
            self.log.debug("Moving averages calculated successfully")
            return df
        except Exception as e:
            self.log.error(f"Error calculating moving averages: {str(e)}")
            return df

    def calculate_signals(self, df):
        """
        Calculate trading signals based on moving average crossover
        Returns DataFrame with additional column for signals
        """
        try:
            # Initialize signals column
            df['signal'] = 0
            
            # Calculate crossover signals
            # 1 for bullish crossover (short MA crosses above long MA)
            # -1 for bearish crossover (short MA crosses below long MA)
            df['signal'] = np.where(
                (df['SMA_short'] > df['SMA_long']) & 
                (df['SMA_short'].shift(1) <= df['SMA_long'].shift(1)),
                1,
                np.where(
                    (df['SMA_short'] < df['SMA_long']) & 
                    (df['SMA_short'].shift(1) >= df['SMA_long'].shift(1)),
                    -1,
                    0
                )
            )
            
            self.log.debug("Trading signals calculated successfully")
            return df
        except Exception as e:
            self.log.error(f"Error calculating signals: {str(e)}")
            return df

    def generate_trade_signal(self, historical_data):
        """
        Generate trading signal based on current market conditions
        Returns: 'BUY', 'SELL', or 'HOLD'
        """
        try:
            if len(historical_data) < self.long_window:
                self.log.warning(f"Not enough data for analysis. Need at least {self.long_window} periods.")
                return 'HOLD'

            # Convert to DataFrame if necessary
            if not isinstance(historical_data, pd.DataFrame):
                df = pd.DataFrame(historical_data)
            else:
                df = historical_data.copy()

            # Calculate indicators
            df = self.calculate_moving_averages(df)
            df = self.calculate_signals(df)

            # Get the latest signal
            current_signal = df['signal'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            # Generate trading decision
            if current_signal == 1 and self.current_position != 'LONG':
                self.log.info(f"Bullish crossover detected at price {current_price}")
                self.current_position = 'LONG'
                return 'BUY'
            elif current_signal == -1 and self.current_position != 'SHORT':
                self.log.info(f"Bearish crossover detected at price {current_price}")
                self.current_position = 'SHORT'
                return 'SELL'
            else:
                return 'HOLD'

        except Exception as e:
            self.log.error(f"Error generating trade signal: {str(e)}")
            return 'HOLD'

    def calculate_metrics(self, df):
        """
        Calculate additional technical indicators and metrics
        Returns DataFrame with additional columns for metrics
        """
        try:
            # Calculate price momentum
            df['momentum'] = df['close'] - df['close'].shift(self.short_window)
            
            # Calculate price volatility (standard deviation)
            df['volatility'] = df['close'].rolling(window=self.short_window).std()
            
            # Calculate trend strength
            df['trend_strength'] = abs(df['SMA_short'] - df['SMA_long']) / df['SMA_long']
            
            self.log.debug("Additional metrics calculated successfully")
            return df
        except Exception as e:
            self.log.error(f"Error calculating additional metrics: {str(e)}")
            return df

    def validate_signal(self, signal, current_price, historical_data):
        """
        Additional validation of the trading signal based on market conditions
        Returns: True if signal is valid, False otherwise
        """
        try:
            df = self.calculate_metrics(historical_data)
            latest = df.iloc[-1]
            
            # Validate based on volatility
            if latest['volatility'] > current_price * 0.05:  # 5% volatility threshold
                self.log.warning("Signal rejected due to high volatility")
                return False
                
            # Validate based on trend strength
            if latest['trend_strength'] < 0.001:  # Minimum trend strength threshold
                self.log.warning("Signal rejected due to weak trend")
                return False
                
            return True
            
        except Exception as e:
            self.log.error(f"Error validating signal: {str(e)}")
            return False

    def reset(self):
        """Reset strategy state"""
        self.current_position = None
        self.log.info("Strategy state reset")
