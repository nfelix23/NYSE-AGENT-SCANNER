"""
Dispersion Scanner Module.
Scans multiple NYSE tickers for investment opportunities based on SMA dispersion.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

from config import TICKERS, SMA_PERIOD, DISPERSION_THRESHOLD, LOOKBACK_DAYS

logger = logging.getLogger(__name__)


def calculate_sma_dispersion(ticker: str, period: int = SMA_PERIOD, days: int = LOOKBACK_DAYS) -> Optional[pd.DataFrame]:
    """
    Calculate the percentage dispersion between close prices and SMA for a ticker.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : int
        SMA period (default: 29)
    days : int
        Number of days of historical data to download

    Returns:
    --------
    pd.DataFrame or None
        DataFrame with Close, SMA, and Dispersion columns, or None if error
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Download data silently
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )

        # Handle MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if data.empty or len(data) < period:
            logger.warning(f"Insufficient data for {ticker}: {len(data)} rows (need {period})")
            return None

        # Calculate SMA
        data[f'SMA_{period}'] = data['Close'].rolling(window=period).mean()

        # Calculate percentage dispersion: ((Close - SMA) / SMA) * 100
        data['Dispersion_%'] = ((data['Close'] - data[f'SMA_{period}']) / data[f'SMA_{period}']) * 100

        # Drop NaN values
        data_clean = data.dropna()

        return data_clean

    except Exception as e:
        logger.error(f"Error processing {ticker}: {str(e)}")
        return None


def get_ticker_dispersion(ticker: str, period: int = SMA_PERIOD) -> Optional[Dict]:
    """
    Get the latest dispersion data for a single ticker.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : int
        SMA period

    Returns:
    --------
    dict or None
        Dictionary with ticker metrics or None if error
    """
    data = calculate_sma_dispersion(ticker, period)

    if data is None or data.empty:
        return None

    latest = data.iloc[-1]
    dispersion = float(latest['Dispersion_%'])

    result = {
        'ticker': ticker,
        'date': data.index[-1].strftime('%Y-%m-%d'),
        'close_price': round(float(latest['Close']), 2),
        f'sma_{period}': round(float(latest[f'SMA_{period}']), 2),
        'dispersion_pct': round(dispersion, 2),
        'signal': classify_signal(dispersion)
    }

    return result


def classify_signal(dispersion: float, threshold: float = DISPERSION_THRESHOLD) -> str:
    """
    Classify the trading signal based on dispersion.

    Parameters:
    -----------
    dispersion : float
        The dispersion percentage
    threshold : float
        The threshold for generating signals

    Returns:
    --------
    str
        'BUY', 'SELL', or 'HOLD'
    """
    if dispersion <= -threshold:
        return 'BUY'  # Price significantly below SMA - potential buying opportunity
    elif dispersion >= threshold:
        return 'SELL'  # Price significantly above SMA - potential selling opportunity
    else:
        return 'HOLD'


def scan_all_tickers(tickers: List[str] = None, period: int = SMA_PERIOD) -> pd.DataFrame:
    """
    Scan all tickers and return a DataFrame with their dispersion metrics.

    Parameters:
    -----------
    tickers : list
        List of ticker symbols (defaults to TICKERS from config)
    period : int
        SMA period

    Returns:
    --------
    pd.DataFrame
        DataFrame with all ticker metrics
    """
    if tickers is None:
        tickers = TICKERS

    results = []
    total = len(tickers)

    logger.info(f"Scanning {total} tickers...")

    for i, ticker in enumerate(tickers, 1):
        logger.info(f"Processing {ticker} ({i}/{total})...")
        result = get_ticker_dispersion(ticker, period)

        if result:
            results.append(result)
        else:
            logger.warning(f"Could not get data for {ticker}")

    if not results:
        logger.warning("No data retrieved for any ticker")
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df = df.sort_values('dispersion_pct', ascending=True)

    return df


def filter_opportunities(df: pd.DataFrame, threshold: float = DISPERSION_THRESHOLD) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filter the scan results to identify buy and sell opportunities.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame from scan_all_tickers
    threshold : float
        Dispersion threshold percentage

    Returns:
    --------
    tuple
        (buy_opportunities, sell_opportunities) DataFrames
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Buy opportunities: dispersion <= -threshold (price below SMA)
    buy_opportunities = df[df['dispersion_pct'] <= -threshold].copy()
    buy_opportunities = buy_opportunities.sort_values('dispersion_pct', ascending=True)

    # Sell opportunities: dispersion >= threshold (price above SMA)
    sell_opportunities = df[df['dispersion_pct'] >= threshold].copy()
    sell_opportunities = sell_opportunities.sort_values('dispersion_pct', ascending=False)

    return buy_opportunities, sell_opportunities


def get_opportunities_summary(tickers: List[str] = None) -> Dict:
    """
    Get a complete summary of all opportunities.

    Parameters:
    -----------
    tickers : list
        List of ticker symbols

    Returns:
    --------
    dict
        Summary with all_data, buy_opportunities, sell_opportunities
    """
    df = scan_all_tickers(tickers)

    if df.empty:
        return {
            'all_data': pd.DataFrame(),
            'buy_opportunities': pd.DataFrame(),
            'sell_opportunities': pd.DataFrame(),
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'tickers_scanned': 0,
            'total_opportunities': 0
        }

    buy_ops, sell_ops = filter_opportunities(df)

    return {
        'all_data': df,
        'buy_opportunities': buy_ops,
        'sell_opportunities': sell_ops,
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tickers_scanned': len(df),
        'total_opportunities': len(buy_ops) + len(sell_ops)
    }


if __name__ == "__main__":
    # Test with a few tickers
    test_tickers = ["AAPL", "MSFT", "GOOGL"]

    print(f"\n{'='*60}")
    print("DISPERSION SCANNER TEST")
    print(f"{'='*60}\n")

    summary = get_opportunities_summary(test_tickers)

    print(f"Scan Time: {summary['scan_time']}")
    print(f"Tickers Scanned: {summary['tickers_scanned']}")
    print(f"Total Opportunities: {summary['total_opportunities']}")

    print(f"\n{'='*60}")
    print("ALL TICKERS:")
    print(f"{'='*60}")
    print(summary['all_data'].to_string(index=False))

    if not summary['buy_opportunities'].empty:
        print(f"\n{'='*60}")
        print("BUY OPPORTUNITIES (Dispersion < -20%):")
        print(f"{'='*60}")
        print(summary['buy_opportunities'].to_string(index=False))

    if not summary['sell_opportunities'].empty:
        print(f"\n{'='*60}")
        print("SELL OPPORTUNITIES (Dispersion > +20%):")
        print(f"{'='*60}")
        print(summary['sell_opportunities'].to_string(index=False))
