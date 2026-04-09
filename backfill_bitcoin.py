#!/usr/bin/env python3
"""Backfill historical Bitcoin (BTC-USD) price data into SQLite database.

Downloads full BTC-USD history from Yahoo Finance starting 2010-07-13
and inserts into the bitcoin_data table.
"""
import sqlite3
import os
import sys
import yfinance as yf

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "oil_markets.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS bitcoin_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_bitcoin_timestamp ON bitcoin_data(timestamp)")
    conn.commit()
    return conn


def backfill():
    conn = init_db()
    c = conn.cursor()

    print("Fetching BTC-USD history from Yahoo Finance...")
    btc = yf.Ticker("BTC-USD")
    hist = btc.history(start="2010-07-13", interval="1d")

    if hist.empty:
        print("No BTC-USD data returned from Yahoo Finance.")
        conn.close()
        return

    # Normalize index (remove timezone)
    hist.index = hist.index.tz_localize(None) if hist.index.tz is not None else hist.index

    print(f"  Got {len(hist)} BTC-USD records from {hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}")

    batch = []
    for date, row in hist.iterrows():
        close_price = float(row['Close'])
        if close_price <= 0:
            continue
        timestamp = date.strftime('%Y-%m-%dT16:00:00.000Z')
        batch.append((timestamp, round(close_price, 2)))

    print(f"Inserting {len(batch)} Bitcoin readings into database...")
    c.executemany(
        "INSERT OR IGNORE INTO bitcoin_data (timestamp, price) VALUES (?, ?)",
        batch
    )
    conn.commit()

    # Verify
    c.execute("SELECT COUNT(*) FROM bitcoin_data")
    total = c.fetchone()[0]
    c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM bitcoin_data")
    min_ts, max_ts = c.fetchone()
    print(f"Done! {total} Bitcoin readings from {min_ts} to {max_ts}")

    conn.close()


if __name__ == "__main__":
    backfill()
