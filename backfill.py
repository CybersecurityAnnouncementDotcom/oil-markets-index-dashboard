#!/usr/bin/env python3
"""Backfill historical oil price data into SQLite database.

Brent data sources:
  - BZ=F (ICE Brent Crude Futures via Yahoo Finance): 2007-07-30 to present
  - FRED DCOILBRENTEU (Europe Brent Spot FOB): 1987 to present (fills pre-2007 gap)
"""
import sqlite3
import os
import sys
import io
import urllib.request
import yfinance as yf
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "oil_markets.db")

FRED_BRENT_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU&cosd=1987-01-01&coed=2030-12-31"

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

def backfill(force=False):
    conn = init_db()
    c = conn.cursor()
    
    # Check if we already have data
    c.execute("SELECT COUNT(*) FROM readings")
    count = c.fetchone()[0]
    if count > 0 and not force:
        print(f"Database already has {count} readings. Skipping backfill.")
        print("Use --force to clear and re-backfill with corrected formulas.")
        conn.close()
        return
    
    if count > 0 and force:
        print(f"Force mode: clearing {count} existing readings...")
        c.execute("DELETE FROM readings")
        conn.commit()
        print("  Old data cleared.")
    
    print("Fetching WTI (CL=F) history...")
    wti = yf.Ticker("CL=F")
    wti_hist = wti.history(period="max", interval="1d")
    print(f"  Got {len(wti_hist)} WTI records from {wti_hist.index[0].strftime('%Y-%m-%d') if len(wti_hist) > 0 else 'N/A'}")
    
    print("Fetching Brent (BZ=F) history from Yahoo Finance...")
    brent = yf.Ticker("BZ=F")
    brent_hist = brent.history(period="max", interval="1d")
    print(f"  Got {len(brent_hist)} BZ=F records from {brent_hist.index[0].strftime('%Y-%m-%d') if len(brent_hist) > 0 else 'N/A'}")
    
    # Normalize indexes to date only (remove timezone)
    wti_hist.index = wti_hist.index.tz_localize(None) if wti_hist.index.tz is not None else wti_hist.index
    brent_hist.index = brent_hist.index.tz_localize(None) if brent_hist.index.tz is not None else brent_hist.index
    
    # Fetch FRED Brent spot prices to fill the pre-2007 gap
    print("Fetching Brent spot prices from FRED (DCOILBRENTEU)...")
    try:
        resp = urllib.request.urlopen(FRED_BRENT_URL)
        fred_csv = resp.read().decode('utf-8')
        fred_df = pd.read_csv(io.StringIO(fred_csv), parse_dates=['observation_date'], index_col='observation_date')
        # FRED uses "." for missing values
        fred_df['DCOILBRENTEU'] = pd.to_numeric(fred_df['DCOILBRENTEU'], errors='coerce')
        fred_df = fred_df.dropna()
        fred_df.index = fred_df.index.tz_localize(None) if fred_df.index.tz is not None else fred_df.index
        print(f"  Got {len(fred_df)} FRED records from {fred_df.index[0].strftime('%Y-%m-%d')} to {fred_df.index[-1].strftime('%Y-%m-%d')}")
        
        # Merge: use BZ=F where available (more accurate futures price), FRED for gaps
        bz_start = brent_hist.index[0] if len(brent_hist) > 0 else pd.Timestamp('2099-01-01')
        fred_pre = fred_df[fred_df.index < bz_start]
        print(f"  Using {len(fred_pre)} FRED records for pre-{bz_start.strftime('%Y-%m-%d')} Brent data")
        
        # Add FRED data to brent_hist as a combined series
        if len(fred_pre) > 0:
            fred_series = fred_pre['DCOILBRENTEU'].rename('Close')
            fred_as_df = pd.DataFrame({'Close': fred_series})
            brent_hist = pd.concat([fred_as_df, brent_hist])
            brent_hist = brent_hist[~brent_hist.index.duplicated(keep='last')]  # prefer BZ=F if overlap
            brent_hist = brent_hist.sort_index()
            print(f"  Combined Brent: {len(brent_hist)} records from {brent_hist.index[0].strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"  WARNING: FRED fetch failed ({e}), pre-2007 Brent will be NULL")
    
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
            composite = (wti_price * 0.3) + (brent_price * 0.7)
        
        index_value = round((composite / 147.0) * 5000, 2)
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
    force = "--force" in sys.argv
    backfill(force=force)
