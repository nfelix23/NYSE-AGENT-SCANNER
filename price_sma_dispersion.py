import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def calculate_sma_dispersion(ticker: str, period: int = 29, start_date: str = None, end_date: str = None):
    """
    Calculate the percentage dispersion between close prices and SMA.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : int
        SMA period (default: 29)
    start_date : str
        Start date in 'YYYY-MM-DD' format
    end_date : str
        End date in 'YYYY-MM-DD' format

    Returns:
    --------
    pd.DataFrame
        DataFrame with Close, SMA, and Dispersion columns
    """
    # Download data
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Handle MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if data.empty:
        raise ValueError(f"No data found for ticker {ticker}")

    # Calculate SMA
    data[f'SMA_{period}'] = data['Close'].rolling(window=period).mean()

    # Calculate percentage dispersion
    # Dispersion = ((Close - SMA) / SMA) * 100
    data['Dispersion_%'] = ((data['Close'] - data[f'SMA_{period}']) / data[f'SMA_{period}']) * 100

    # Drop NaN values from SMA calculation
    data_clean = data.dropna()

    return data_clean

def get_latest_dispersion(ticker: str, period: int = 29):
    """
    Get the latest price and SMA dispersion percentage.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : int
        SMA period (default: 29)

    Returns:
    --------
    dict
        Dictionary with latest metrics
    """
    data = calculate_sma_dispersion(ticker, period)

    latest = data.iloc[-1]

    result = {
        'ticker': ticker,
        'date': data.index[-1].strftime('%Y-%m-%d'),
        'last_price': round(latest['Close'], 2),
        f'sma_{period}': round(latest[f'SMA_{period}'], 2),
        'dispersion_%': round(latest['Dispersion_%'], 2),
        'direction': 'Above SMA' if latest['Dispersion_%'] > 0 else 'Below SMA'
    }

    return result

def plot_dispersion(ticker: str, period: int = 29, start_date: str = None):
    """
    Plot close prices, SMA, and dispersion.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : int
        SMA period (default: 29)
    start_date : str
        Start date in 'YYYY-MM-DD' format
    """
    data = calculate_sma_dispersion(ticker, period, start_date)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Plot 1: Price and SMA
    ax1.plot(data.index, data['Close'], label='Close Price', color='blue', linewidth=1.5)
    ax1.plot(data.index, data[f'SMA_{period}'], label=f'SMA {period}', color='orange', linewidth=1.5)
    ax1.fill_between(data.index, data['Close'], data[f'SMA_{period}'],
                     where=data['Close'] >= data[f'SMA_{period}'],
                     alpha=0.3, color='green', label='Above SMA')
    ax1.fill_between(data.index, data['Close'], data[f'SMA_{period}'],
                     where=data['Close'] < data[f'SMA_{period}'],
                     alpha=0.3, color='red', label='Below SMA')

    # Add current dispersion % as text annotation
    current_disp = data['Dispersion_%'].iloc[-1]
    current_price = data['Close'].iloc[-1]
    ax1.text(0.02, 0.98, f'Current Dispersion: {current_disp:.2f}%',
             transform=ax1.transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    ax1.set_ylabel('Price', fontsize=12)
    ax1.set_title(f'{ticker} - Close Price vs SMA {period}', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Dispersion percentage
    ax2.plot(data.index, data['Dispersion_%'], label='Dispersion %', color='purple', linewidth=1.5)
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax2.fill_between(data.index, 0, data['Dispersion_%'],
                     where=data['Dispersion_%'] >= 0,
                     alpha=0.3, color='green')
    ax2.fill_between(data.index, 0, data['Dispersion_%'],
                     where=data['Dispersion_%'] < 0,
                     alpha=0.3, color='red')

    # Add min and max dispersion annotations
    max_disp = data['Dispersion_%'].max()
    min_disp = data['Dispersion_%'].min()
    ax2.text(0.02, 0.98, f'Max: {max_disp:.2f}%\nMin: {min_disp:.2f}%\nCurrent: {current_disp:.2f}%',
             transform=ax2.transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Dispersion %', fontsize=12)
    ax2.set_title(f'Percentage Dispersion from SMA {period}', fontsize=14, fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{ticker}_dispersion_analysis.png', dpi=300, bbox_inches='tight')
    print(f"Plot saved as {ticker}_dispersion_analysis.png")
    plt.show()

def dispersion_statistics(ticker: str, period: int = 29, start_date: str = None):
    """
    Calculate dispersion statistics.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : int
        SMA period (default: 29)
    start_date : str
        Start date in 'YYYY-MM-DD' format

    Returns:
    --------
    dict
        Dictionary with dispersion statistics
    """
    data = calculate_sma_dispersion(ticker, period, start_date)

    stats = {
        'mean_dispersion_%': round(data['Dispersion_%'].mean(), 2),
        'std_dispersion_%': round(data['Dispersion_%'].std(), 2),
        'max_dispersion_%': round(data['Dispersion_%'].max(), 2),
        'min_dispersion_%': round(data['Dispersion_%'].min(), 2),
        'current_dispersion_%': round(data['Dispersion_%'].iloc[-1], 2),
        'days_above_sma': int((data['Dispersion_%'] > 0).sum()),
        'days_below_sma': int((data['Dispersion_%'] < 0).sum()),
        'total_days': len(data)
    }

    return stats

# Example usage
if __name__ == "__main__":
    # Configuration
    TICKER = "GGAL"  # Change to your desired ticker
    SMA_PERIOD = 29
    START_DATE = "2024-01-01"  # Optional: specify start date

    print(f"\n{'='*60}")
    print(f"SMA DISPERSION ANALYSIS - {TICKER}")
    print(f"{'='*60}\n")

    # Get latest dispersion
    print("📊 Latest Dispersion Metrics:")
    print("-" * 60)
    latest = get_latest_dispersion(TICKER, SMA_PERIOD)
    for key, value in latest.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Get statistics
    print(f"\n📈 Historical Dispersion Statistics:")
    print("-" * 60)
    stats = dispersion_statistics(TICKER, SMA_PERIOD, START_DATE)
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Calculate percentage of time above/below SMA
    pct_above = (stats['days_above_sma'] / stats['total_days']) * 100
    pct_below = (stats['days_below_sma'] / stats['total_days']) * 100
    print(f"\nPercentage Above SMA: {pct_above:.2f}%")
    print(f"Percentage Below SMA: {pct_below:.2f}%")

    # Plot
    print(f"\n📉 Generating visualization...")
    print("-" * 60)
    plot_dispersion(TICKER, SMA_PERIOD, START_DATE)

    # Show detailed data (last 10 days)
    print(f"\n📋 Last 10 Days Data:")
    print("-" * 60)
    data = calculate_sma_dispersion(TICKER, SMA_PERIOD, START_DATE)
    display_cols = ['Close', f'SMA_{SMA_PERIOD}', 'Dispersion_%']
    print(data[display_cols].tail(10).to_string())
