#!/usr/bin/env python3
"""
Fast Export Generator for Oil Markets Index Pro subscribers.
Reads from SQLite DB and writes CSV/JSON files to data/exports/.

Run via nightly-export.sh cron or manually:
  python3 generate_exports.py

Generates:
  data/exports/daily/YYYY-MM-DD.csv
  data/exports/daily/YYYY-MM-DD.json
  data/exports/oil-markets-latest.csv
  data/exports/oil-markets-latest.json
  data/exports/oil-markets-history.csv
  data/exports/oil-markets-history.json

NOTE: Data starts from 2000-08-23 (earliest WTI data from Yahoo Finance CL=F).

Performance: Uses dictionary-based lookups instead of correlated subqueries.
Previous version used a correlated subquery (SELECT ... FROM bitcoin_data WHERE
date(bd.timestamp) = date(r.timestamp)) inside the main GROUP BY query, causing
O(N*M) full table scans that hung the e2-micro VPS at 90%+ CPU for 8+ minutes.
The fix pre-builds a date->price dictionary for bitcoin_data, then does O(1)
lookups per row. This matches the approach used by Bitcoin and Gold export scripts.
"""

import sqlite3
import json
import csv
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "data" / "oil_markets.db"
EXPORT_DIR = SCRIPT_DIR / "data" / "exports"
DAILY_DIR = EXPORT_DIR / "daily"

# Data start date: earliest WTI data from Yahoo Finance CL=F
DATA_START_DATE = "2000-08-23"

# Ensure export directories exist
DAILY_DIR.mkdir(parents=True, exist_ok=True)

CSV_FIELDS = ["date", "index_value", "wti_price", "brent_price", "bitcoin_price"]


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def write_csv(filepath, rows, fieldnames):
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written: {filepath} ({len(rows)} rows)")


def write_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Written: {filepath}")


def main():
    print(f"[{datetime.utcnow().isoformat()}] Generating Oil Markets Index exports (fast mode)...")
    print(f"  DB: {DB_PATH}")
    print(f"  Export dir: {EXPORT_DIR}")
    print(f"  Data start date: {DATA_START_DATE}")
    print()

    conn = get_db()

    # Step 1: Build bitcoin price lookup dictionary (fast, one query)
    btc_map = {}
    for r in conn.execute("""
        SELECT date(timestamp) as d, price
        FROM bitcoin_data
        WHERE timestamp IN (
            SELECT MAX(timestamp) FROM bitcoin_data GROUP BY date(timestamp)
        )
    """).fetchall():
        btc_map[r['d']] = r['price']
    print(f"  Bitcoin: {len(btc_map)} daily prices loaded")

    # Step 2: Get one reading per calendar day from readings table (no correlated subquery)
    rows = conn.execute("""
        SELECT date(timestamp) as date,
               MAX(timestamp) as timestamp,
               value as index_value,
               wti_price,
               brent_price
        FROM readings
        WHERE date(timestamp) >= ?
        GROUP BY date(timestamp)
        ORDER BY date ASC
    """, (DATA_START_DATE,)).fetchall()
    print(f"  Readings: {len(rows)} daily rows (from {DATA_START_DATE})")
    print()

    # Step 3: Build combined rows using O(1) dictionary lookup for BTC
    csv_rows = []
    json_data = []

    for r in rows:
        d = r['date']
        btc_price = btc_map.get(d)

        row = {
            "date": d,
            "index_value": round(r["index_value"], 2),
            "wti_price": round(r["wti_price"], 2) if r["wti_price"] else "",
            "brent_price": round(r["brent_price"], 2) if r["brent_price"] else "",
            "bitcoin_price": round(btc_price, 2) if btc_price else "",
        }
        csv_rows.append(row)
        json_data.append({
            "date": d,
            "timestamp": r["timestamp"],
            "index_value": round(r["index_value"], 2),
            "wti_price": round(r["wti_price"], 2) if r["wti_price"] else None,
            "brent_price": round(r["brent_price"], 2) if r["brent_price"] else None,
            "bitcoin_price": round(btc_price, 2) if btc_price else None,
        })

    # Step 4: Write history files
    print("1. Full history:")
    write_csv(EXPORT_DIR / "oil-markets-history.csv", csv_rows, CSV_FIELDS)
    write_json(EXPORT_DIR / "oil-markets-history.json", {
        "export_date": datetime.utcnow().isoformat(),
        "record_count": len(json_data),
        "data": json_data,
    })
    print()

    # Step 5: Write latest files
    print("2. Latest files:")
    if csv_rows:
        latest_csv = csv_rows[-1]
        latest_json = json_data[-1]
        write_csv(EXPORT_DIR / "oil-markets-latest.csv", [latest_csv], CSV_FIELDS)
        write_json(EXPORT_DIR / "oil-markets-latest.json", {
            "export_date": datetime.utcnow().isoformat(),
            **latest_json,
        })
    else:
        print("  No readings found")
    print()

    # Step 6: Write daily snapshot
    today = datetime.utcnow().strftime("%Y-%m-%d")
    print(f"3. Daily snapshot for {today}:")
    today_rows = [r for r in csv_rows if r["date"] == today]
    today_json = [j for j in json_data if j["date"] == today]
    if today_rows:
        write_csv(DAILY_DIR / f"{today}.csv", today_rows, CSV_FIELDS)
        write_json(DAILY_DIR / f"{today}.json", today_json[-1])
    else:
        print(f"  No data for {today}, skipping daily snapshot")
    print()

    conn.close()
    print("Export generation complete.")


if __name__ == "__main__":
    main()
