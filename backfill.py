#!/usr/bin/env python3
"""Backfill historical oil price data into SQLite database."""
import sqlite3
import os
import sys
import yfinance as yf
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "oil_markets.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            value REAL NOT NULL,
            wti_price REAL,
            brent_price REAL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp)")
    conn.commit()
    return conn

def backfill():
    conn = init_db()
    c = conn.cursor()
    
    # Check if we already have data
    c.execute("SELECT COUNT(*) FROM readings")
    count = c.fetchone()[0]
    if count > 0:
        print(f"Database already has {count} readings. Skipping backfill.")
        conn.close()
        return
    
    print("Fetching WTI (CL=F) history...")
    wti = yf.Ticker("CL=F")
    wti_hist = wti.history(period="max", interval="1d")
    print(f"  Got {len(wti_hist)} WTI records from {wti_hist.index[0].strftime('%Y-%m-%d') if len(wti_hist) > 0 else 'N/A'}")
    
    print("Fetching Brent (BZ=F) history...")
    brent = yf.Ticker("BZ=F")
    brent_hist = brent.history(period="max", interval="1d")
    print(f"  Got {len(brent_hist)} Brent records from {brent_hist.index[0].strftime('%Y-%m-%d') if len(brent_hist) > 0 else 'N/A'}")
    
    # Normalize indexes to date only (remove timezone)
    wti_hist.index = wti_hist.index.tz_localize(None) if wti_hist.index.tz is not None else wti_hist.index
    brent_hist.index = brent_hist.index.tz_localize(None) if brent_hist.index.tz is not None else brent_hist.index
    
    # Create a combined date range
    all_dates = sorted(set(wti_hist.index.tolist() + brent_hist.index.tolist()))
    
    print(f"Processing {len(all_dates)} trading days...")
    
    batch = []
    for date in all_dates:
        wti_price = None
        brent_price = None
        
        if date in wti_hist.index:
            wti_price = float(wti_hist.loc[date, 'Close'])
            if pd.isna(wti_price) or wti_price <= 0:
                wti_price = None
        
        if date in brent_hist.index:
            brent_price = float(brent_hist.loc[date, 'Close'])
            if pd.isna(brent_price) or brent_price <= 0:
                brent_price = None
        
        # Skip if no valid prices
        if wti_price is None and brent_price is None:
            continue
        
        # For pre-Brent era, use WTI as 100% proxy
        if brent_price is None:
            composite = wti_price
        elif wti_price is None:
            composite = brent_price
        else:
            composite = (wti_price * 0.4) + (brent_price * 0.6)
        
        index_value = round((composite / 147.0) * 50000, 2)
        timestamp = date.strftime('%Y-%m-%dT16:00:00.000Z')
        
        batch.append((timestamp, index_value, wti_price, brent_price))
    
    print(f"Inserting {len(batch)} readings into database...")
    c.executemany(
        "INSERT INTO readings (timestamp, value, wti_price, brent_price) VALUES (?, ?, ?, ?)",
        batch
    )
    conn.commit()
    
    # Verify
    c.execute("SELECT COUNT(*) FROM readings")
    total = c.fetchone()[0]
    c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM readings")
    min_ts, max_ts = c.fetchone()
    print(f"Done! {total} readings from {min_ts} to {max_ts}")
    
    conn.close()

if __name__ == "__main__":
    backfill()
