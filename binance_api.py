from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import pandas as pd
import numpy as np
import random
import config
import logger
from datetime import datetime

class BinanceClient:
    def __init__(self):
        """Initialize Binance client with API credentials"""
        self.log = logger.get_logger()
        
        if config.SIMULATION_MODE:
            self.client = None
            self.log.info("Initialized in simulation mode - no API connection required")
        else:
            try:
                self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
                self.log.info("Binance client initialized successfully")
            except Exception as e:
                self.log.error(f"Failed to initialize Binance client: {str(e)}")
                raise

    def get_current_price(self, symbol=config.TARGET_SYMBOL):
        """Get current price for a symbol"""
        try:
            if config.SIMULATION_MODE:
                # Generate a realistic test price around 30000 USD for BTC
                import random
                base_price = 30000
                variation = base_price * 0.001  # 0.1% variation
                price = base_price + random.uniform(-variation, variation)
                self.log.debug(f"Simulation: Generated price for {symbol}: {price}")
                return price
            
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.log.debug(f"Current {symbol} price: {price}")
            return price
        except BinanceAPIException as e:
            self.log.error(f"Binance API error getting price: {str(e)}")
            return None
        except Exception as e:
            self.log.error(f"Unexpected error getting price: {str(e)}")
            return None

    def get_historical_prices(self, symbol=config.TARGET_SYMBOL, interval='1m', limit=500):
        """
        Get historical kline/candlestick data
        Returns DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            if config.SIMULATION_MODE:
                # Generate realistic test data
                import numpy as np
                from datetime import datetime, timedelta
                
                base_price = 30000
                timestamps = [datetime.now() - timedelta(minutes=i) for i in range(limit-1, -1, -1)]
                
                # Generate prices with random walk
                prices = [base_price]
                for _ in range(limit-1):
                    change = np.random.normal(0, base_price * 0.001)  # 0.1% standard deviation
                    new_price = prices[-1] + change
                    prices.append(new_price)
                
                # Create simulated klines data
                klines = []
                for i in range(limit):
                    price = prices[i]
                    kline = [
                        int(timestamps[i].timestamp() * 1000),  # timestamp
                        str(price * 0.998),  # open
                        str(price * 1.002),  # high
                        str(price * 0.997),  # low
                        str(price),          # close
                        str(random.uniform(0.1, 2.0)),  # volume
                        int(timestamps[i].timestamp() * 1000),  # close time
                        str(price * random.uniform(0.1, 2.0)),  # quote volume
                        100,  # trades
                        str(random.uniform(0.05, 1.0)),  # taker buy base
                        str(price * random.uniform(0.05, 1.0)),  # taker buy quote
                        "0"  # ignored
                    ]
                    klines.append(kline)
                
                self.log.debug(f"Simulation: Generated {len(klines)} historical prices")
            else:
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignored'
            ])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            self.log.debug(f"Retrieved {len(df)} historical prices for {symbol}")
            return df
            
        except BinanceAPIException as e:
            self.log.error(f"Binance API error getting historical data: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            self.log.error(f"Unexpected error getting historical data: {str(e)}")
            return pd.DataFrame()

    def place_order(self, symbol, side, quantity):
        """
        Place a market order
        side: 'BUY' or 'SELL'
        """
        if config.SIMULATION_MODE:
            self.log.info(f"SIMULATION: {side} order for {quantity} {symbol}")
            return {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'status': 'SIMULATED',
                'price': self.get_current_price(symbol)
            }
        
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            self.log.info(f"Order placed: {side} {quantity} {symbol}")
            return order
        except BinanceAPIException as e:
            self.log.error(f"Binance API error placing order: {str(e)}")
            return None
        except Exception as e:
            self.log.error(f"Unexpected error placing order: {str(e)}")
            return None

    def get_account_balance(self, asset='USDT'):
        """Get current balance for a specific asset"""
        try:
            if config.SIMULATION_MODE:
                self.log.info(f"SIMULATION: Using mock balance of {config.SIMULATION_BALANCE} {asset}")
                return config.SIMULATION_BALANCE
                
            account = self.client.get_account()
            balance = next(
                (float(b['free']) for b in account['balances'] if b['asset'] == asset),
                0.0
            )
            self.log.info(f"Current {asset} balance: {balance}")
            return balance
        except BinanceAPIException as e:
            self.log.error(f"Binance API error getting balance: {str(e)}")
            return 0.0
        except Exception as e:
            self.log.error(f"Unexpected error getting balance: {str(e)}")
            return 0.0

    def get_exchange_info(self, symbol=config.TARGET_SYMBOL):
        """Get exchange information for symbol"""
        try:
            info = self.client.get_exchange_info()
            symbol_info = next(
                (s for s in info['symbols'] if s['symbol'] == symbol),
                None
            )
            if symbol_info:
                self.log.debug(f"Retrieved exchange info for {symbol}")
                return symbol_info
            else:
                self.log.error(f"Symbol {symbol} not found in exchange info")
                return None
        except BinanceAPIException as e:
            self.log.error(f"Binance API error getting exchange info: {str(e)}")
            return None
        except Exception as e:
            self.log.error(f"Unexpected error getting exchange info: {str(e)}")
            return None

    def check_api_connection(self):
        """Test API connection and permissions"""
        if config.SIMULATION_MODE:
            self.log.info("Running in simulation mode - API connection test skipped")
            return True
            
        if self.client is None:
            self.log.error("Binance client not initialized")
            return False
            
        try:
            self.client.get_account()
            self.log.info("API connection test successful")
            return True
        except BinanceAPIException as e:
            self.log.error(f"API connection test failed: {str(e)}")
            return False
        except Exception as e:
            self.log.error(f"Unexpected error testing API connection: {str(e)}")
            return False
