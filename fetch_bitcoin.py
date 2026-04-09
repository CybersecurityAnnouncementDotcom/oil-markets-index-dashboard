#!/usr/bin/env python3
"""Fetch current Bitcoin (BTC-USD) price using yfinance."""
import json
import sys
import yfinance as yf

def fetch_price():
    try:
        btc = yf.Ticker("BTC-USD")

        btc_info = btc.fast_info
        btc_price = float(btc_info.last_price) if hasattr(btc_info, 'last_price') and btc_info.last_price else None

        # Fallback: try history
        if btc_price is None:
            hist = btc.history(period="1d")
            if not hist.empty:
                btc_price = float(hist['Close'].iloc[-1])

        if btc_price is None:
            print(json.dumps({"error": "Could not fetch Bitcoin price"}))
            sys.exit(1)

        result = {
            "bitcoin_price": round(btc_price, 2)
        }

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    fetch_price()
