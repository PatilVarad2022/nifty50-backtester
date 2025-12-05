import yfinance as yf
import pandas as pd
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'data_raw.csv')

def fetch_data(ticker='^NSEI', start_date='2015-01-01', end_date=None):
    """
    Fetches data from yfinance or loads from local CSV if it exists.
    If end_date is None, defaults to today's date for real-time data.
    """
    # Default to today if not specified
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    if os.path.exists(DATA_PATH):
        print(f"Loading data from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
        # Filter by date just in case the cached file has different range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        return df
    
    print(f"Downloading data for {ticker}...")
    df = yf.download(ticker, start=start_date, end=end_date)
    
    if df.empty:
        raise ValueError(f"No data found for {ticker}")

    # Ensure we have a flat index if MultiIndex is returned (common with new yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    # Keep only necessary columns
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # Save to CSV
    df.to_csv(DATA_PATH)
    return df

if __name__ == "__main__":
    df = fetch_data()
    print(df.head())
    print(df.tail())
