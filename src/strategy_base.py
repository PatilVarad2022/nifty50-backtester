from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    """
    Base class for all trading strategies.
    Ensures consistent interface and extensibility.
    """
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on strategy logic.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional 'Signal' column (1 = Long, 0 = Flat)
        """
        raise NotImplementedError("Strategy must implement generate_signals()")
    
    def validate_data(self, data: pd.DataFrame, min_rows: int = 200):
        """
        Validate that data has sufficient rows for strategy.
        """
        if len(data) < min_rows:
            raise ValueError(f"Insufficient data: {len(data)} rows. Need at least {min_rows}.")
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
