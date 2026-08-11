import os
import requests
import yfinance as yf
from datetime import datetime

# The Discord Webhook URL is securely pulled from GitHub Secrets
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Define your Staging Area Watchlist here
# Format: {"ticker": "TARGET_PRICE"}
WATCHLIST = {
    "SOAR": 3.00
}

# The threshold percentage (1.5% in the dashboard)
ZONE_THRESHOLD = 0.015 

def send_discord_alert(ticker, live_price, target_price):
    """Sends a formatted message to a Discord Webhook."""
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    message = (
        f"🚨 **STAGING ZONE ALERT** 🚨\n\n"
        f"**{ticker}** has entered the Strike Zone!\n"
        f"Live Price: **${live_price:.2f}**\n"
        f"Target HVN: **${target_price:.2f}**\n\n"
        f"*Time to open the Options Protocol Dashboard and run the Perfect Entry Checklist!*"
    )

    payload = {"content": message}
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"Successfully sent alert for {ticker}")
    except Exception as e:
        print(f"Failed to send Discord alert for {ticker}: {e}")

def main():
    print(f"Starting scan at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    
    if not WATCHLIST:
        print("Watchlist is empty. Exiting.")
        return

    # Fetch live data for all tickers at once using yfinance
    tickers_string = " ".join(WATCHLIST.keys())
    print(f"Fetching data for: {tickers_string}")
    
    try:
        # yfinance downloads data for all requested tickers
        data = yf.download(tickers_string, period="1d", interval="1m", progress=False)
    except Exception as e:
        print(f"Failed to fetch market data: {e}")
        return

    for ticker, target_price in WATCHLIST.items():
        try:
            # Handle yfinance data structure (differs slightly if 1 ticker vs multiple)
            if len(WATCHLIST) == 1:
                live_price = data['Close'].iloc[-1]
            else:
                live_price = data['Close'][ticker].iloc[-1]
            
            # Ensure we have a valid number
            if not isinstance(live_price, (int, float)):
                live_price = float(live_price.iloc[0]) # Fallback for pandas series weirdness

            distance = abs(live_price - target_price)
            pct_away = distance / live_price
            
            print(f"[{ticker}] Live: ${live_price:.2f} | Target: ${target_price:.2f} | Diff: {pct_away*100:.2f}%")

            # If the price is within 1.5% of the target HVN, fire the alert
            if pct_away <= ZONE_THRESHOLD:
                print(f"  -> {ticker} IS IN THE ZONE! Triggering alert...")
                send_discord_alert(ticker, float(live_price), target_price)
                
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    print("Scan complete.")

if __name__ == "__main__":
    main()
