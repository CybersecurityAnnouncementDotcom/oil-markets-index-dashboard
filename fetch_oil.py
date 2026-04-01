#!/usr/bin/env python3
"""Fetch current WTI and Brent crude oil prices using yfinance."""
import json
import sys
import yfinance as yf

def fetch_prices():
    try:
        wti = yf.Ticker("CL=F")
        brent = yf.Ticker("BZ=F")
        
        wti_info = wti.fast_info
        brent_info = brent.fast_info
        
        wti_price = float(wti_info.last_price) if hasattr(wti_info, 'last_price') and wti_info.last_price else None
        brent_price = float(brent_info.last_price) if hasattr(brent_info, 'last_price') and brent_info.last_price else None
        
        # Fallback: try history
        if wti_price is None:
            hist = wti.history(period="1d")
            if not hist.empty:
                wti_price = float(hist['Close'].iloc[-1])
        
        if brent_price is None:
            hist = brent.history(period="1d")
            if not hist.empty:
                brent_price = float(hist['Close'].iloc[-1])
        
        if wti_price is None and brent_price is None:
            print(json.dumps({"error": "Could not fetch any prices"}))
            sys.exit(1)
        
        # If one is missing, use the other as proxy
        if wti_price is None:
            wti_price = brent_price
        if brent_price is None:
            brent_price = wti_price
        
        # Calculate composite index
        composite = (wti_price * 0.4) + (brent_price * 0.6)
        index_value = round((composite / 147.0) * 5000, 2)
        
        result = {
            "wti_price": round(wti_price, 2),
            "brent_price": round(brent_price, 2),
            "composite_price": round(composite, 2),
            "index_value": index_value
        }
        
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    fetch_prices()
