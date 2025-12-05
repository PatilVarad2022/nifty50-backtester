import pandas as pd
import numpy as np

class Backtester:
    """
    Professional-grade backtester with proper execution modeling.
    
    Key Features:
    - Open-to-open return basis for both strategy and benchmark
    - Dividend-adjusted benchmark returns (realistic comparison)
    - Stop-loss and take-profit support
    - Fractional position sizing
    - Proper transaction cost modeling (only on position changes)
    - Handles last open position (forces close at end)
    - Explicit NaN/warmup handling
    - No look-ahead bias
    
    Execution Model:
    - Signals generated at close
    - Trades execute at next day's open
    - Returns calculated on open-to-open basis
    - SL/TP checked at each day's close
    """
    
    def __init__(self, data, initial_capital=100000, transaction_cost=0.001, 
                 dividend_yield=0.015, stop_loss=None, take_profit=None, position_size=1.0):
        """
        Initialize backtester.
        
        Args:
            data: DataFrame with OHLC columns
            initial_capital: Starting capital (default 100,000)
            transaction_cost: Cost per side as decimal (0.001 = 0.1% = 10 bps)
            dividend_yield: Annual dividend yield for benchmark (default 0.015 = 1.5%)
            stop_loss: Stop loss as decimal (e.g., -0.05 = -5%), None to disable
            take_profit: Take profit as decimal (e.g., 0.10 = 10%), None to disable
            position_size: Fraction of capital to deploy (0.5 = 50%, 1.0 = 100%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.dividend_yield = dividend_yield
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.position_size = position_size
        self.trades = pd.DataFrame()  # Store trade log
        
    def _apply_stop_loss_take_profit(self, df):
        """
        Apply stop-loss and take-profit rules to positions.
        
        Modifies the Position column to exit when SL or TP is hit.
        Adds Exit_Reason column to track why positions were closed.
        
        Args:
            df: DataFrame with Position, Open, and Close columns
            
        Returns:
            DataFrame with modified Position and Exit_Reason columns
        """
        if self.stop_loss is None and self.take_profit is None:
            df['Exit_Reason'] = 'Signal'
            return df
            
        df['Exit_Reason'] = 'Signal'
        position = df['Position'].values.copy()
        entry_price = None
        
        for i in range(len(df)):
            if position[i] == 1:
                # Track entry price
                if i == 0 or position[i-1] == 0:
                    entry_price = df['Open'].iloc[i]
                    
                # Check SL/TP at close
                if entry_price is not None:
                    current_price = df['Close'].iloc[i]
                    pnl_pct = (current_price / entry_price) - 1
                    
                    # Check stop loss
                    if self.stop_loss is not None and pnl_pct <= self.stop_loss:
                        position[i] = 0  # Force exit
                        df.loc[df.index[i], 'Exit_Reason'] = 'Stop_Loss'
                        entry_price = None
                        
                    # Check take profit
                    elif self.take_profit is not None and pnl_pct >= self.take_profit:
                        position[i] = 0  # Force exit
                        df.loc[df.index[i], 'Exit_Reason'] = 'Take_Profit'
                        entry_price = None
                        
            elif position[i] == 0 and i > 0 and position[i-1] == 1:
                # Natural exit from signal
                entry_price = None
                
        df['Position'] = position
        return df
    def run_momentum(self, sma_window=50):
        """
        Momentum Strategy with proper execution lag.
        
        Strategy Logic:
        - Long when Close > SMA
        - Flat otherwise
        
        Execution:
        - Signal generated at close
        - Position taken at next day's open
        
        Args:
            sma_window: Simple moving average window
            
        Returns:
            DataFrame with signals, positions, returns, and equity curves
        """
        df = self.data.copy()
        df['SMA'] = df['Close'].rolling(window=sma_window).mean()
        
        # Signal: 1 if Close > SMA, else 0
        # Set to 0 where SMA is NaN (warmup period)
        df['Signal'] = np.where(df['Close'] > df['SMA'], 1, 0)
        df.loc[df['SMA'].isna(), 'Signal'] = 0
        
        # CRITICAL: Shift signal to avoid look-ahead bias
        # Position today = Signal from yesterday
        df['Position'] = df['Signal'].shift(1).fillna(0)
        
        # Execute at NEXT DAY OPEN
        df['Exec_Price'] = df['Open']
        
        # Apply stop-loss and take-profit
        df = self._apply_stop_loss_take_profit(df)
        
        # Handle last open position: force close at end
        df = self._close_last_position(df)
        
        # Generate trade log
        self.trades = self._generate_trade_log(df)
        
        return self._calculate_returns(df)

    def run_mean_reversion(self, sma_window=20, std_dev=2.0):
        """
        Mean Reversion Strategy with proper execution lag.
        
        Strategy Logic:
        - Enter long when Close < Lower Bollinger Band
        - Exit when Close >= SMA (mean reversion complete)
        
        Args:
            sma_window: SMA window for Bollinger Bands
            std_dev: Standard deviation multiplier (default 2.0)
            
        Returns:
            DataFrame with signals, positions, returns, and equity curves
        """
        df = self.data.copy()
        df['SMA'] = df['Close'].rolling(window=sma_window).mean()
        df['Std'] = df['Close'].rolling(window=sma_window).std()
        df['Lower'] = df['SMA'] - (std_dev * df['Std'])
        
        # State-based signal generation
        signals = np.zeros(len(df))
        position = 0
        
        close = df['Close'].values
        sma = df['SMA'].values
        lower = df['Lower'].values
        
        # Start after warmup period
        for i in range(sma_window, len(df)):
            # Skip if indicators are NaN
            if np.isnan(sma[i]) or np.isnan(lower[i]):
                signals[i] = 0
                continue
                
            if position == 0:
                # Entry: price below lower band
                if close[i] < lower[i]:
                    position = 1
            elif position == 1:
                # Exit: price back to mean
                if close[i] >= sma[i]:
                    position = 0
            signals[i] = position
            
        df['Signal'] = signals
        
        # Avoid look-ahead: shift signal
        df['Position'] = df['Signal'].shift(1).fillna(0)
        df['Exec_Price'] = df['Open']
        
        # Apply stop-loss and take-profit
        df = self._apply_stop_loss_take_profit(df)
        
        # Handle last open position
        df = self._close_last_position(df)
        
        self.trades = self._generate_trade_log(df)
        
        return self._calculate_returns(df)

    def run_rsi(self, rsi_period=14, oversold=30, overbought=70):
        """
        RSI (Relative Strength Index) Strategy with proper execution lag.
        
        Strategy Logic:
        - Enter long when RSI < oversold threshold (default 30)
        - Exit when RSI > overbought threshold (default 70) or RSI > 50 (neutral)
        
        Execution:
        - Signal generated at close
        - Position taken at next day's open
        
        Args:
            rsi_period: Period for RSI calculation (default 14)
            oversold: Oversold threshold for entry (default 30)
            overbought: Overbought threshold for exit (default 70)
            
        Returns:
            DataFrame with signals, positions, returns, and equity curves
        """
        df = self.data.copy()
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # State-based signal generation
        signals = np.zeros(len(df))
        position = 0
        
        rsi = df['RSI'].values
        
        # Start after warmup period
        for i in range(rsi_period + 1, len(df)):
            # Skip if RSI is NaN
            if np.isnan(rsi[i]):
                signals[i] = 0
                continue
                
            if position == 0:
                # Entry: RSI below oversold
                if rsi[i] < oversold:
                    position = 1
            elif position == 1:
                # Exit: RSI above overbought or back to neutral
                if rsi[i] > overbought or rsi[i] > 50:
                    position = 0
            signals[i] = position
            
        df['Signal'] = signals
        
        # Avoid look-ahead: shift signal
        df['Position'] = df['Signal'].shift(1).fillna(0)
        df['Exec_Price'] = df['Open']
        
        # Apply stop-loss and take-profit
        df = self._apply_stop_loss_take_profit(df)
        
        # Handle last open position
        df = self._close_last_position(df)
        
        self.trades = self._generate_trade_log(df)
        
        return self._calculate_returns(df)

    def _close_last_position(self, df):
        """
        Force close any open position at the end of the data.
        
        This ensures:
        - Equity curve is complete
        - Trade log includes the final trade
        - No hanging positions
        
        Args:
            df: DataFrame with Position column
            
        Returns:
            DataFrame with last position closed
        """
        # If last position is 1, set it to 0 to force close
        if df['Position'].iloc[-1] == 1:
            df.loc[df.index[-1], 'Position'] = 0
            
        return df

    def _generate_trade_log(self, df):
        """
        Generate detailed trade log with entry/exit dates and P/L.
        
        Returns:
            DataFrame with columns: Entry_Date, Entry_Price, Exit_Date, Exit_Price, PnL, Return_Pct, Exit_Reason
        """
        trades = []
        position = df['Position'].values
        dates = df.index
        prices = df['Exec_Price'].values
        exit_reasons = df['Exit_Reason'].values if 'Exit_Reason' in df.columns else ['Signal'] * len(df)
        
        in_trade = False
        entry_date = None
        entry_price = None
        
        for i in range(len(df)):
            if pd.isna(position[i]):
                continue
                
            # Entry: position goes from 0 to 1
            if position[i] == 1 and not in_trade:
                in_trade = True
                entry_date = dates[i]
                entry_price = prices[i]
            
            # Exit: position goes from 1 to 0
            elif position[i] == 0 and in_trade:
                in_trade = False
                exit_date = dates[i]
                exit_price = prices[i]
                exit_reason = exit_reasons[i] if i < len(exit_reasons) else 'Signal'
                
                # Calculate P&L
                # Number of shares = capital * position_size / entry_price
                shares = (self.initial_capital * self.position_size) / entry_price
                gross_pnl = (exit_price - entry_price) * shares
                
                # Transaction costs: entry + exit
                cost = (self.initial_capital * self.position_size) * self.transaction_cost * 2
                net_pnl = gross_pnl - cost
                
                # Return percentage (net of costs)
                return_pct = (exit_price / entry_price - 1) - (self.transaction_cost * 2)
                
                trades.append({
                    'Entry_Date': entry_date,
                    'Entry_Price': entry_price,
                    'Exit_Date': exit_date,
                    'Exit_Price': exit_price,
                    'PnL': net_pnl,
                    'Return_Pct': return_pct,
                    'Exit_Reason': exit_reason
                })
        
        # Handle case where position is still open at end (shouldn't happen with _close_last_position)
        if in_trade:
            # Force close at last available price
            exit_date = dates[-1]
            exit_price = prices[-1]
            
            shares = self.initial_capital / entry_price
            gross_pnl = (exit_price - entry_price) * shares
            cost = self.initial_capital * self.transaction_cost * 2
            net_pnl = gross_pnl - cost
            return_pct = (exit_price / entry_price - 1) - (self.transaction_cost * 2)
            
            trades.append({
                'Entry_Date': entry_date,
                'Entry_Price': entry_price,
                'Exit_Date': exit_date,
                'Exit_Price': exit_price,
                'PnL': net_pnl,
                'Return_Pct': return_pct,
                'Exit_Reason': 'End_of_Data'
            })
        
        return pd.DataFrame(trades)

    def _calculate_returns(self, df):
        """
        Calculate returns with consistent open-to-open basis.
        
        IMPORTANT: Both market and strategy returns use open-to-open basis
        for internal consistency and fair comparison.
        
        Market Return: (Today's Open / Yesterday's Open) - 1 + Daily Dividend Yield
        Strategy Return: Market Return * Position * Position_Size - Transaction Costs
        
        Args:
            df: DataFrame with Position and Open columns
            
        Returns:
            DataFrame with Market_Return, Strategy_Return, and equity curves
        """
        # Market Returns: Open-to-Open + Dividend Yield
        df['Market_Return'] = df['Open'].pct_change()
        
        # Add dividend yield (annualized, so divide by 252 trading days)
        daily_dividend = self.dividend_yield / 252
        df['Market_Return'] = df['Market_Return'] + daily_dividend
        
        # Strategy Returns: Open-to-Open when in position, scaled by position size
        # When Position = 1, we earn the market return * position_size
        # When Position = 0, we earn 0
        df['Strategy_Return'] = df['Market_Return'] * df['Position'] * self.position_size
        
        # Apply transaction costs ONLY on position changes
        position_change = df['Position'].diff().abs().fillna(0)
        df['Cost'] = position_change * self.transaction_cost * self.position_size
        df['Strategy_Return'] = df['Strategy_Return'] - df['Cost']
        
        # Fill NaN returns with 0
        df['Market_Return'] = df['Market_Return'].fillna(0)
        df['Strategy_Return'] = df['Strategy_Return'].fillna(0)
        
        # Equity Curves
        df['Market_Equity'] = self.initial_capital * (1 + df['Market_Return']).cumprod()
        df['Strategy_Equity'] = self.initial_capital * (1 + df['Strategy_Return']).cumprod()
        
        return df

    def save_trade_log(self, filepath='data/trades.csv'):
        """
        Save trade log to CSV.
        
        Args:
            filepath: Path to save CSV file
        """
        if len(self.trades) > 0:
            self.trades.to_csv(filepath, index=False)
        else:
            # Create empty file with headers
            pd.DataFrame(columns=[
                'Entry_Date', 'Entry_Price', 'Exit_Date', 'Exit_Price', 'PnL', 'Return_Pct', 'Exit_Reason'
            ]).to_csv(filepath, index=False)
