import sqlite3
import pandas as pd
from datetime import datetime
import config
import logger
import os

class Database:
    def __init__(self):
        """Initialize database connection and create tables if they don't exist"""
        self.log = logger.get_logger()
        self.db_path = config.DB_FILENAME
        self.initialize_database()

    def initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL NOT NULL,
                    status TEXT NOT NULL,
                    pnl REAL,
                    stop_loss REAL,
                    take_profit REAL
                )
            ''')

            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    total_trades INTEGER NOT NULL,
                    winning_trades INTEGER NOT NULL,
                    losing_trades INTEGER NOT NULL,
                    win_rate REAL NOT NULL,
                    total_profit_loss REAL NOT NULL,
                    sharpe_ratio REAL,
                    max_drawdown REAL
                )
            ''')

            conn.commit()
            self.log.info("Database initialized successfully")

        except sqlite3.Error as e:
            self.log.error(f"Database initialization error: {str(e)}")
        finally:
            if conn:
                conn.close()

    def insert_trade(self, trade_data):
        """
        Insert a new trade record
        trade_data: dictionary containing trade information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO trades (
                    timestamp, symbol, side, quantity, price, 
                    total_value, status, pnl, stop_loss, take_profit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                trade_data['symbol'],
                trade_data['side'],
                trade_data['quantity'],
                trade_data['price'],
                trade_data['quantity'] * trade_data['price'],
                trade_data['status'],
                trade_data.get('pnl', None),
                trade_data.get('stop_loss', None),
                trade_data.get('take_profit', None)
            ))

            conn.commit()
            self.log.info(f"Trade record inserted successfully: {trade_data['side']} {trade_data['quantity']} {trade_data['symbol']}")

        except sqlite3.Error as e:
            self.log.error(f"Error inserting trade record: {str(e)}")
        finally:
            if conn:
                conn.close()

    def update_trade_pnl(self, trade_id, pnl):
        """Update the PnL for a specific trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE trades 
                SET pnl = ? 
                WHERE id = ?
            ''', (pnl, trade_id))

            conn.commit()
            self.log.info(f"Updated PnL for trade {trade_id}: {pnl}")

        except sqlite3.Error as e:
            self.log.error(f"Error updating trade PnL: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_trade_history(self, limit=100):
        """
        Retrieve recent trade history
        Returns: pandas DataFrame of trades
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(limit,))
            self.log.info(f"Retrieved {len(df)} trade records")
            return df

        except sqlite3.Error as e:
            self.log.error(f"Error retrieving trade history: {str(e)}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

    def insert_performance_metrics(self, metrics):
        """Insert performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO performance_metrics (
                    timestamp, total_trades, winning_trades, losing_trades,
                    win_rate, total_profit_loss, sharpe_ratio, max_drawdown
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                metrics['total_trades'],
                metrics['winning_trades'],
                metrics['losing_trades'],
                metrics['win_rate'],
                metrics['total_profit_loss'],
                metrics.get('sharpe_ratio', None),
                metrics.get('max_drawdown', None)
            ))

            conn.commit()
            self.log.info("Performance metrics inserted successfully")

        except sqlite3.Error as e:
            self.log.error(f"Error inserting performance metrics: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_performance_metrics(self, days=30):
        """
        Retrieve performance metrics for the specified number of days
        Returns: pandas DataFrame of metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT * FROM performance_metrics 
                WHERE timestamp >= date('now', ?) 
                ORDER BY timestamp DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
            self.log.info(f"Retrieved performance metrics for the last {days} days")
            return df

        except sqlite3.Error as e:
            self.log.error(f"Error retrieving performance metrics: {str(e)}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

    def calculate_daily_pnl(self):
        """
        Calculate daily PnL from trade history
        Returns: pandas DataFrame with daily PnL
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT 
                    date(timestamp) as date,
                    SUM(pnl) as daily_pnl,
                    COUNT(*) as num_trades
                FROM trades 
                WHERE pnl IS NOT NULL
                GROUP BY date(timestamp)
                ORDER BY date DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            self.log.info("Daily PnL calculated successfully")
            return df

        except sqlite3.Error as e:
            self.log.error(f"Error calculating daily PnL: {str(e)}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

    def get_win_rate(self):
        """Calculate overall win rate"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades
                FROM trades 
                WHERE pnl IS NOT NULL
            ''')

            total_trades, winning_trades = cursor.fetchone()
            
            if total_trades > 0:
                win_rate = winning_trades / total_trades
                self.log.info(f"Current win rate: {win_rate:.2%}")
                return win_rate
            return 0.0

        except sqlite3.Error as e:
            self.log.error(f"Error calculating win rate: {str(e)}")
            return 0.0
        finally:
            if conn:
                conn.close()

    def cleanup_old_records(self, days=30):
        """Remove records older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM trades 
                WHERE timestamp < date('now', ?)
            ''', (f'-{days} days',))

            cursor.execute('''
                DELETE FROM performance_metrics 
                WHERE timestamp < date('now', ?)
            ''', (f'-{days} days',))

            conn.commit()
            self.log.info(f"Cleaned up records older than {days} days")

        except sqlite3.Error as e:
            self.log.error(f"Error cleaning up old records: {str(e)}")
        finally:
            if conn:
                conn.close()
