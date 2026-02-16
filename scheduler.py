"""
Scheduler Module.
Automatically runs the NYSE stock scanner at specified times daily.
"""
import schedule
import time
import logging
from datetime import datetime
import sys

from main import run_scan
from config import TICKERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def scheduled_scan():
    """
    Scheduled scan job that runs the full analysis and sends email alerts.
    Only executes on weekdays (Monday to Friday).
    """
    # Check if today is a weekday (0=Monday, 6=Sunday)
    today = datetime.now().weekday()
    day_name = datetime.now().strftime('%A')

    if today >= 5:  # Saturday (5) or Sunday (6)
        logger.info("="*70)
        logger.info(f"SCAN SKIPPED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Today is {day_name} (weekend) - Market is closed")
        logger.info("Next scan will run on Monday")
        logger.info("="*70 + "\n")
        return

    logger.info("="*70)
    logger.info(f"SCHEDULED SCAN STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S (%A)')}")
    logger.info("="*70)

    try:
        # Run the scan with email enabled and chart generation
        summary = run_scan(
            tickers=TICKERS,
            send_email=True,
            test_mode=False,
            generate_charts=True,
            charts_dir="daily_charts"
        )

        logger.info(f"Scheduled scan completed successfully")
        logger.info(f"Tickers scanned: {summary['tickers_scanned']}")
        logger.info(f"Opportunities found: {summary['total_opportunities']}")

    except Exception as e:
        logger.error(f"Error during scheduled scan: {str(e)}", exc_info=True)

    logger.info("="*70)
    logger.info(f"SCHEDULED SCAN FINISHED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70 + "\n")


def run_scheduler(scan_time: str = "09:00"):
    """
    Start the scheduler to run scans at specified time daily.

    Parameters:
    -----------
    scan_time : str
        Time to run the scan in HH:MM format (24-hour)
    """
    logger.info("="*70)
    logger.info("NYSE STOCK SCANNER - SCHEDULER STARTED")
    logger.info("="*70)
    logger.info(f"Scheduled scan time: {scan_time} (Monday-Friday only)")
    logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S (%A)')}")
    logger.info("Market hours: Weekdays only (Saturday & Sunday will be skipped)")
    logger.info("Press Ctrl+C to stop the scheduler")
    logger.info("="*70 + "\n")

    # Schedule the job
    schedule.every().day.at(scan_time).do(scheduled_scan)

    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        logger.info("\n" + "="*70)
        logger.info("SCHEDULER STOPPED BY USER")
        logger.info("="*70)
        sys.exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='NYSE Stock Scanner Scheduler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scheduler.py                    # Run weekdays at 09:00 (default)
  python scheduler.py --time 14:30       # Run weekdays at 14:30
  python scheduler.py --run-now          # Run immediately and then continue schedule
  python scheduler.py --once             # Run once and exit (no scheduling)

Note: Scans only run Monday-Friday (market days). Weekend runs are automatically skipped.
        """
    )

    parser.add_argument(
        '--time',
        type=str,
        default='09:00',
        help='Time to run daily scan in HH:MM format (default: 09:00)'
    )

    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run scan immediately before starting schedule'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Run scan once and exit (no scheduling)'
    )

    args = parser.parse_args()

    # Validate time format
    try:
        datetime.strptime(args.time, '%H:%M')
    except ValueError:
        print("Error: Invalid time format. Use HH:MM (e.g., 09:00, 14:30)")
        sys.exit(1)

    # Run once mode
    if args.once:
        logger.info("Running scan once...")
        scheduled_scan()
        sys.exit(0)

    # Run immediately if requested
    if args.run_now:
        logger.info("Running initial scan immediately...")
        scheduled_scan()
        logger.info("\n")

    # Start scheduler
    run_scheduler(args.time)
