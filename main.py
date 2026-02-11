"""
NYSE Investment Opportunity Detection Agent - Main Script.

This script orchestrates the scanning of NYSE stocks for investment opportunities
based on price dispersion from the 29-day Simple Moving Average (SMA).

Usage:
    python main.py              # Run full scan and send email if opportunities found
    python main.py --test       # Test mode with 3 tickers (no email)
    python main.py --no-email   # Run scan without sending email
    python main.py --test-email # Send a test email to verify configuration
    python main.py --charts     # Generate individual charts for each stock
"""
import argparse
import logging
from datetime import datetime
import sys

from config import TICKERS, SMA_PERIOD, DISPERSION_THRESHOLD, LOG_FILE
from dispersion_scanner import get_opportunities_summary, scan_all_tickers
from email_alerts import send_alert, send_test_email
from visualization import generate_all_charts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print application banner."""
    banner = """
================================================================
     NYSE Investment Opportunity Detection Agent
     SMA Dispersion Analysis
================================================================
    """
    print(banner)


def print_summary(summary: dict):
    """Print a formatted summary of the scan results."""
    print(f"\n{'='*60}")
    print("SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Scan Time: {summary['scan_time']}")
    print(f"Tickers Scanned: {summary['tickers_scanned']}")
    print(f"SMA Period: {SMA_PERIOD} days")
    print(f"Dispersion Threshold: +/-{DISPERSION_THRESHOLD}%")
    print(f"Total Opportunities: {summary['total_opportunities']}")

    all_data = summary.get('all_data')
    buy_ops = summary.get('buy_opportunities')
    sell_ops = summary.get('sell_opportunities')

    # Print all tickers
    if not all_data.empty:
        print(f"\n{'='*60}")
        print("ALL TICKERS:")
        print(f"{'='*60}")
        print(f"{'Ticker':<8} {'Close':>10} {'SMA-29':>10} {'Dispersion':>12} {'Signal':>8}")
        print("-" * 60)
        for _, row in all_data.iterrows():
            disp_sign = "+" if row['dispersion_pct'] > 0 else ""
            print(f"{row['ticker']:<8} ${row['close_price']:>9.2f} ${row[f'sma_{SMA_PERIOD}']:>9.2f} {disp_sign}{row['dispersion_pct']:>10.2f}% {row['signal']:>8}")

    # Print buy opportunities
    if not buy_ops.empty:
        print(f"\n{'='*60}")
        print("BUY OPPORTUNITIES (Price significantly BELOW SMA):")
        print(f"{'='*60}")
        for _, row in buy_ops.iterrows():
            print(f"  {row['ticker']}: ${row['close_price']:.2f} (Dispersion: {row['dispersion_pct']:.2f}%)")
    else:
        print(f"\nNo BUY opportunities detected (dispersion > -{DISPERSION_THRESHOLD:.1f}%)")

    # Print sell opportunities
    if not sell_ops.empty:
        print(f"\n{'='*60}")
        print("SELL OPPORTUNITIES (Price significantly ABOVE SMA):")
        print(f"{'='*60}")
        for _, row in sell_ops.iterrows():
            print(f"  {row['ticker']}: ${row['close_price']:.2f} (Dispersion: +{row['dispersion_pct']:.2f}%)")
    else:
        print(f"\nNo SELL opportunities detected (dispersion < +{DISPERSION_THRESHOLD:.1f}%)")


def run_scan(tickers: list = None, send_email: bool = True, test_mode: bool = False,
             generate_charts: bool = False, charts_dir: str = "charts") -> dict:
    """
    Run the dispersion scan and optionally send email alerts.

    Parameters:
    -----------
    tickers : list
        List of tickers to scan (defaults to config TICKERS)
    send_email : bool
        Whether to send email alerts
    test_mode : bool
        If True, use only 3 tickers for testing
    generate_charts : bool
        If True, generate individual charts for each stock
    charts_dir : str
        Directory to save charts

    Returns:
    --------
    dict
        Scan summary
    """
    print_banner()

    # Use test tickers if in test mode
    if test_mode:
        tickers = ["AAPL", "MSFT", "GOOGL"]
        logger.info("Running in TEST MODE with 3 tickers")
    elif tickers is None:
        tickers = TICKERS

    logger.info(f"Starting scan of {len(tickers)} tickers...")
    logger.info(f"Configuration: SMA-{SMA_PERIOD}, Threshold: +/-{DISPERSION_THRESHOLD}%")

    # Run the scan
    summary = get_opportunities_summary(tickers)

    # Print results
    print_summary(summary)

    # Generate charts if requested
    if generate_charts:
        logger.info("Generating individual charts for each stock...")
        chart_summary = generate_all_charts(tickers, output_dir=charts_dir)
        print(f"\n{'='*60}")
        print("CHART GENERATION RESULTS")
        print(f"{'='*60}")
        print(f"Total charts: {chart_summary['total']}")
        print(f"Successful: {chart_summary['successful']}")
        print(f"Failed: {chart_summary['failed']}")
        print(f"Output directory: {chart_summary['output_directory']}")

        if chart_summary['successful_tickers']:
            print(f"\nCharts generated for: {', '.join(chart_summary['successful_tickers'])}")

    # Send email if opportunities found and email is enabled
    if send_email and not test_mode:
        if summary['total_opportunities'] > 0:
            logger.info("Opportunities detected, sending email alert...")
            if send_alert(summary):
                logger.info("Email alert sent successfully!")
            else:
                logger.warning("Failed to send email alert")
        else:
            logger.info("No opportunities detected, skipping email")
    elif test_mode:
        logger.info("Test mode: Email sending disabled")

    # Log completion
    logger.info(f"Scan completed. Found {summary['total_opportunities']} opportunities.")

    return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='NYSE Investment Opportunity Detection Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full scan and send email
  python main.py --test             # Test mode with 3 tickers
  python main.py --no-email         # Run scan without sending email
  python main.py --test-email       # Send a test email
  python main.py --charts           # Run scan and generate charts
  python main.py --charts --test    # Test with 3 tickers and generate charts
        """
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: scan only 3 tickers, no email'
    )

    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Run scan without sending email alerts'
    )

    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Send a test email to verify configuration'
    )

    parser.add_argument(
        '--tickers',
        type=str,
        help='Comma-separated list of tickers to scan (e.g., AAPL,MSFT,GOOGL)'
    )

    parser.add_argument(
        '--charts',
        action='store_true',
        help='Generate individual charts for each stock'
    )

    parser.add_argument(
        '--charts-dir',
        type=str,
        default='charts',
        help='Directory to save charts (default: charts)'
    )

    args = parser.parse_args()

    # Handle test email mode
    if args.test_email:
        print_banner()
        logger.info("Sending test email...")
        if send_test_email():
            print("\nTest email sent successfully!")
            return 0
        else:
            print("\nFailed to send test email. Check your .env configuration.")
            return 1

    # Parse custom tickers if provided
    tickers = None
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
        logger.info(f"Using custom tickers: {tickers}")

    # Run the scan
    try:
        summary = run_scan(
            tickers=tickers,
            send_email=not args.no_email,
            test_mode=args.test,
            generate_charts=args.charts,
            charts_dir=args.charts_dir
        )

        return 0 if summary['tickers_scanned'] > 0 else 1

    except KeyboardInterrupt:
        logger.info("\nScan interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
