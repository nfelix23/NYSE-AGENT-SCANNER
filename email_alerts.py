"""
Email Alerts Module.
Sends email notifications for detected investment opportunities.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import pandas as pd
import logging
from datetime import datetime

from config import EMAIL_CONFIG, SMA_PERIOD, DISPERSION_THRESHOLD

logger = logging.getLogger(__name__)


def create_html_email(summary: Dict) -> str:
    """
    Create an HTML formatted email with the opportunities summary.

    Parameters:
    -----------
    summary : dict
        Summary dictionary from get_opportunities_summary

    Returns:
    --------
    str
        HTML formatted email body
    """
    buy_ops = summary.get('buy_opportunities', pd.DataFrame())
    sell_ops = summary.get('sell_opportunities', pd.DataFrame())
    all_data = summary.get('all_data', pd.DataFrame())
    scan_time = summary.get('scan_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                margin-top: 30px;
            }}
            .summary-box {{
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .buy {{
                color: #27ae60;
                font-weight: bold;
            }}
            .sell {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .hold {{
                color: #7f8c8d;
            }}
            .alert-buy {{
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }}
            .alert-sell {{
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <h1>NYSE Investment Opportunity Alert</h1>

        <div class="summary-box">
            <strong>Scan Time:</strong> {scan_time}<br>
            <strong>Tickers Analyzed:</strong> {summary.get('tickers_scanned', 0)}<br>
            <strong>SMA Period:</strong> {SMA_PERIOD} days<br>
            <strong>Dispersion Threshold:</strong> +/-{DISPERSION_THRESHOLD}%<br>
            <strong>Total Opportunities Found:</strong> {summary.get('total_opportunities', 0)}
        </div>
    """

    # Buy Opportunities Section
    if not buy_ops.empty:
        html += """
        <h2>BUY Opportunities</h2>
        <div class="alert-buy">
            <strong>Signal:</strong> Price significantly BELOW moving average - potential buying opportunity
        </div>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Close Price</th>
                <th>SMA-29</th>
                <th>Dispersion %</th>
                <th>Signal</th>
            </tr>
        """
        for _, row in buy_ops.iterrows():
            html += f"""
            <tr>
                <td><strong>{row['ticker']}</strong></td>
                <td>${row['close_price']:.2f}</td>
                <td>${row[f'sma_{SMA_PERIOD}']:.2f}</td>
                <td class="buy">{row['dispersion_pct']:.2f}%</td>
                <td class="buy">{row['signal']}</td>
            </tr>
            """
        html += "</table>"
    else:
        html += """
        <h2>BUY Opportunities</h2>
        <p>No buy opportunities detected at this time.</p>
        """

    # Sell Opportunities Section
    if not sell_ops.empty:
        html += """
        <h2>SELL Opportunities</h2>
        <div class="alert-sell">
            <strong>Signal:</strong> Price significantly ABOVE moving average - potential selling opportunity
        </div>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Close Price</th>
                <th>SMA-29</th>
                <th>Dispersion %</th>
                <th>Signal</th>
            </tr>
        """
        for _, row in sell_ops.iterrows():
            html += f"""
            <tr>
                <td><strong>{row['ticker']}</strong></td>
                <td>${row['close_price']:.2f}</td>
                <td>${row[f'sma_{SMA_PERIOD}']:.2f}</td>
                <td class="sell">+{row['dispersion_pct']:.2f}%</td>
                <td class="sell">{row['signal']}</td>
            </tr>
            """
        html += "</table>"
    else:
        html += """
        <h2>SELL Opportunities</h2>
        <p>No sell opportunities detected at this time.</p>
        """

    # All Tickers Summary
    if not all_data.empty:
        html += """
        <h2>All Tickers Summary</h2>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Close Price</th>
                <th>SMA-29</th>
                <th>Dispersion %</th>
                <th>Signal</th>
            </tr>
        """
        for _, row in all_data.iterrows():
            signal_class = row['signal'].lower()
            disp_sign = "+" if row['dispersion_pct'] > 0 else ""
            html += f"""
            <tr>
                <td><strong>{row['ticker']}</strong></td>
                <td>${row['close_price']:.2f}</td>
                <td>${row[f'sma_{SMA_PERIOD}']:.2f}</td>
                <td class="{signal_class}">{disp_sign}{row['dispersion_pct']:.2f}%</td>
                <td class="{signal_class}">{row['signal']}</td>
            </tr>
            """
        html += "</table>"

    html += """
        <div class="footer">
            <p>
                <strong>Disclaimer:</strong> This is an automated alert for informational purposes only.
                This is not financial advice. Always do your own research before making investment decisions.
            </p>
            <p>
                Generated by NYSE Investment Opportunity Detection Agent
            </p>
        </div>
    </body>
    </html>
    """

    return html


def create_plain_text_email(summary: Dict) -> str:
    """
    Create a plain text formatted email.

    Parameters:
    -----------
    summary : dict
        Summary dictionary from get_opportunities_summary

    Returns:
    --------
    str
        Plain text email body
    """
    buy_ops = summary.get('buy_opportunities', pd.DataFrame())
    sell_ops = summary.get('sell_opportunities', pd.DataFrame())
    all_data = summary.get('all_data', pd.DataFrame())
    scan_time = summary.get('scan_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    text = f"""
NYSE INVESTMENT OPPORTUNITY ALERT
{'='*50}

Scan Time: {scan_time}
Tickers Analyzed: {summary.get('tickers_scanned', 0)}
SMA Period: {SMA_PERIOD} days
Dispersion Threshold: +/-{DISPERSION_THRESHOLD}%
Total Opportunities Found: {summary.get('total_opportunities', 0)}

"""

    if not buy_ops.empty:
        text += f"""
{'='*50}
BUY OPPORTUNITIES (Price below SMA)
{'='*50}
"""
        for _, row in buy_ops.iterrows():
            text += f"""
Ticker: {row['ticker']}
  Close: ${row['close_price']:.2f}
  SMA-{SMA_PERIOD}: ${row[f'sma_{SMA_PERIOD}']:.2f}
  Dispersion: {row['dispersion_pct']:.2f}%
  Signal: {row['signal']}
"""

    if not sell_ops.empty:
        text += f"""
{'='*50}
SELL OPPORTUNITIES (Price above SMA)
{'='*50}
"""
        for _, row in sell_ops.iterrows():
            text += f"""
Ticker: {row['ticker']}
  Close: ${row['close_price']:.2f}
  SMA-{SMA_PERIOD}: ${row[f'sma_{SMA_PERIOD}']:.2f}
  Dispersion: +{row['dispersion_pct']:.2f}%
  Signal: {row['signal']}
"""

    text += f"""
{'='*50}
ALL TICKERS SUMMARY
{'='*50}
"""
    if not all_data.empty:
        for _, row in all_data.iterrows():
            disp_sign = "+" if row['dispersion_pct'] > 0 else ""
            text += f"{row['ticker']:6} | ${row['close_price']:>8.2f} | {disp_sign}{row['dispersion_pct']:>6.2f}% | {row['signal']}\n"

    text += """
---
Disclaimer: This is an automated alert for informational purposes only.
This is not financial advice. Always do your own research.
"""

    return text


def send_alert(summary: Dict, test_mode: bool = False) -> bool:
    """
    Send an email alert with the opportunities summary.

    Parameters:
    -----------
    summary : dict
        Summary dictionary from get_opportunities_summary
    test_mode : bool
        If True, only print the email without sending

    Returns:
    --------
    bool
        True if email sent successfully, False otherwise
    """
    # Check email configuration
    sender_email = EMAIL_CONFIG.get('sender_email')
    sender_password = EMAIL_CONFIG.get('sender_password')
    recipient_email = EMAIL_CONFIG.get('recipient_email')

    if not all([sender_email, sender_password, recipient_email]):
        logger.error("Email configuration incomplete. Please check .env file.")
        logger.info("Required: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT")
        return False

    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"NYSE Alert: {summary.get('total_opportunities', 0)} Opportunities Detected - {summary.get('scan_time', '')}"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Create both plain text and HTML versions
    text_content = create_plain_text_email(summary)
    html_content = create_html_email(summary)

    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')

    msg.attach(part1)
    msg.attach(part2)

    if test_mode:
        logger.info("TEST MODE - Email would be sent with the following content:")
        print(text_content)
        return True

    try:
        smtp_server = EMAIL_CONFIG.get('smtp_server', 'smtp.gmail.com')
        smtp_port = EMAIL_CONFIG.get('smtp_port', 587)

        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed. Check your email credentials.")
        logger.info("For Gmail, use an App Password: https://myaccount.google.com/apppasswords")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def send_test_email() -> bool:
    """
    Send a test email to verify configuration.

    Returns:
    --------
    bool
        True if test email sent successfully
    """
    test_summary = {
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tickers_scanned': 3,
        'total_opportunities': 2,
        'all_data': pd.DataFrame([
            {'ticker': 'TEST1', 'close_price': 100.0, f'sma_{SMA_PERIOD}': 120.0, 'dispersion_pct': -16.67, 'signal': 'HOLD'},
            {'ticker': 'TEST2', 'close_price': 150.0, f'sma_{SMA_PERIOD}': 120.0, 'dispersion_pct': 25.0, 'signal': 'SELL'},
            {'ticker': 'TEST3', 'close_price': 80.0, f'sma_{SMA_PERIOD}': 100.0, 'dispersion_pct': -20.0, 'signal': 'BUY'},
        ]),
        'buy_opportunities': pd.DataFrame([
            {'ticker': 'TEST3', 'close_price': 80.0, f'sma_{SMA_PERIOD}': 100.0, 'dispersion_pct': -20.0, 'signal': 'BUY'},
        ]),
        'sell_opportunities': pd.DataFrame([
            {'ticker': 'TEST2', 'close_price': 150.0, f'sma_{SMA_PERIOD}': 120.0, 'dispersion_pct': 25.0, 'signal': 'SELL'},
        ]),
    }

    logger.info("Sending test email...")
    return send_alert(test_summary)


if __name__ == "__main__":
    print("Testing email module...")
    print("Attempting to send test email...")

    success = send_test_email()

    if success:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Check your configuration.")
