"""
Visualization Module.
Creates individual charts for each stock showing price, SMA, and dispersion.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import pandas as pd
import numpy as np
from typing import List, Optional
import logging
from datetime import datetime
import os

from config import SMA_PERIOD, DISPERSION_THRESHOLD, LOOKBACK_DAYS
from dispersion_scanner import calculate_sma_dispersion

logger = logging.getLogger(__name__)


def create_stock_chart(ticker: str, data: pd.DataFrame, period: int = SMA_PERIOD,
                       save_path: Optional[str] = None) -> bool:
    """
    Create a comprehensive chart for a single stock showing:
    - Price and SMA
    - Dispersion percentage
    - Buy/Sell zones

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    data : pd.DataFrame
        DataFrame with Close, SMA, and Dispersion columns
    period : int
        SMA period used
    save_path : str, optional
        Path to save the chart image

    Returns:
    --------
    bool
        True if chart created successfully
    """
    try:
        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10))
        gs = GridSpec(3, 1, height_ratios=[2, 1, 0.5], hspace=0.3)

        # Get latest values
        latest = data.iloc[-1]
        latest_close = latest['Close']
        latest_sma = latest[f'SMA_{period}']
        latest_dispersion = latest['Dispersion_%']

        # Determine signal
        if latest_dispersion <= -DISPERSION_THRESHOLD:
            signal = 'BUY'
            signal_color = 'green'
        elif latest_dispersion >= DISPERSION_THRESHOLD:
            signal = 'SELL'
            signal_color = 'red'
        else:
            signal = 'HOLD'
            signal_color = 'gray'

        # Subplot 1: Price and SMA
        ax1 = fig.add_subplot(gs[0])
        ax1.plot(data.index, data['Close'], label='Close Price', color='#2E86AB', linewidth=2)
        ax1.plot(data.index, data[f'SMA_{period}'], label=f'SMA-{period}',
                color='#A23B72', linewidth=2, linestyle='--')

        # Fill area between price and SMA
        ax1.fill_between(data.index, data['Close'], data[f'SMA_{period}'],
                        where=(data['Close'] >= data[f'SMA_{period}']),
                        alpha=0.3, color='red', label='Above SMA')
        ax1.fill_between(data.index, data['Close'], data[f'SMA_{period}'],
                        where=(data['Close'] < data[f'SMA_{period}']),
                        alpha=0.3, color='green', label='Below SMA')

        # Mark latest point
        ax1.scatter(data.index[-1], latest_close, color=signal_color, s=100,
                   zorder=5, edgecolors='black', linewidths=2)

        ax1.set_title(f'{ticker} - Price Analysis | Signal: {signal}',
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left', framealpha=0.9)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Add text box with current values and configuration
        textstr = (f'Close: ${latest_close:.2f}\n'
                  f'SMA-{period}: ${latest_sma:.2f}\n'
                  f'Dispersion: {latest_dispersion:.2f}%\n'
                  f'---\n'
                  f'Threshold: ±{DISPERSION_THRESHOLD}%\n'
                  f'Lookback: {LOOKBACK_DAYS} days')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)
        ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
                verticalalignment='top', bbox=props, family='monospace')

        # Subplot 2: Dispersion Percentage
        ax2 = fig.add_subplot(gs[1], sharex=ax1)

        # Color the dispersion line based on value
        colors = np.where(data['Dispersion_%'] >= DISPERSION_THRESHOLD, 'red',
                         np.where(data['Dispersion_%'] <= -DISPERSION_THRESHOLD, 'green', 'gray'))

        # Plot dispersion as bars
        ax2.bar(data.index, data['Dispersion_%'], color=colors, alpha=0.6, width=0.8)

        # Add threshold lines
        ax2.axhline(y=DISPERSION_THRESHOLD, color='red', linestyle='--',
                   linewidth=2, label=f'Sell Threshold (+{DISPERSION_THRESHOLD}%)')
        ax2.axhline(y=-DISPERSION_THRESHOLD, color='green', linestyle='--',
                   linewidth=2, label=f'Buy Threshold (-{DISPERSION_THRESHOLD}%)')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)

        # Fill zones
        ax2.fill_between(data.index, DISPERSION_THRESHOLD, ax2.get_ylim()[1],
                        alpha=0.1, color='red', label='SELL Zone')
        ax2.fill_between(data.index, -DISPERSION_THRESHOLD, ax2.get_ylim()[0],
                        alpha=0.1, color='green', label='BUY Zone')

        ax2.set_ylabel('Dispersion (%)', fontsize=12, fontweight='bold')
        ax2.set_title(f'Price Dispersion from SMA-{period} (Threshold: ±{DISPERSION_THRESHOLD}%)',
                     fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left', framealpha=0.9, fontsize=9)
        ax2.grid(True, alpha=0.3)

        # Subplot 3: Signal Indicator
        ax3 = fig.add_subplot(gs[2])
        ax3.axis('off')

        # Create signal box
        signal_text = f'SIGNAL: {signal}'
        ax3.text(0.5, 0.5, signal_text,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=20, fontweight='bold',
                color='white',
                bbox=dict(boxstyle='round,pad=1',
                         facecolor=signal_color,
                         edgecolor='black',
                         linewidth=3))

        # Format x-axis
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Add timestamp and configuration info
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        config_text = (f'Config: SMA-{period} | Threshold: ±{DISPERSION_THRESHOLD}% | '
                      f'Lookback: {LOOKBACK_DAYS} days | Generated: {timestamp}')
        fig.text(0.5, 0.01, config_text,
                ha='center', va='bottom', fontsize=8, style='italic', alpha=0.7)

        # Save or show
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            logger.info(f"Chart saved to {save_path}")
        else:
            plt.tight_layout()
            plt.show()

        plt.close()
        return True

    except Exception as e:
        logger.error(f"Error creating chart for {ticker}: {str(e)}")
        return False


def generate_all_charts(tickers: List[str], output_dir: str = "charts") -> dict:
    """
    Generate individual charts for multiple tickers.

    Parameters:
    -----------
    tickers : list
        List of ticker symbols
    output_dir : str
        Directory to save charts

    Returns:
    --------
    dict
        Summary with successful and failed chart generations
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    successful = []
    failed = []

    logger.info(f"Generating charts for {len(tickers)} tickers...")

    for i, ticker in enumerate(tickers, 1):
        logger.info(f"Generating chart {i}/{len(tickers)}: {ticker}")

        # Get data
        data = calculate_sma_dispersion(ticker)

        if data is None or data.empty:
            logger.warning(f"No data available for {ticker}")
            failed.append(ticker)
            continue

        # Create chart
        save_path = os.path.join(output_dir, f"{ticker}_analysis.png")
        success = create_stock_chart(ticker, data, save_path=save_path)

        if success:
            successful.append(ticker)
        else:
            failed.append(ticker)

    summary = {
        'total': len(tickers),
        'successful': len(successful),
        'failed': len(failed),
        'successful_tickers': successful,
        'failed_tickers': failed,
        'output_directory': output_dir
    }

    logger.info(f"Chart generation complete: {len(successful)}/{len(tickers)} successful")

    return summary


if __name__ == "__main__":
    # Test with a few tickers
    from config import TICKERS

    print("\n" + "="*60)
    print("CHART GENERATION TEST")
    print("="*60 + "\n")

    # Test with first 3 tickers
    test_tickers = TICKERS[:3]

    summary = generate_all_charts(test_tickers, output_dir="test_charts")

    print(f"\nResults:")
    print(f"  Total tickers: {summary['total']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Output directory: {summary['output_directory']}")

    if summary['successful_tickers']:
        print(f"\nSuccessful charts: {', '.join(summary['successful_tickers'])}")

    if summary['failed_tickers']:
        print(f"Failed charts: {', '.join(summary['failed_tickers'])}")
