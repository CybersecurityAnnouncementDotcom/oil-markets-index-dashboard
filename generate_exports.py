#!/usr/bin/env python3
"""
Daily Export Generator for Oil Markets Index Pro subscribers.
Reads from SQLite DB and writes CSV/JSON files to data/exports/.

Run via PM2 cron or manually:
  python3 generate_exports.py

Generates:
  data/exports/daily/YYYY-MM-DD.csv
  data/exports/daily/YYYY-MM-DD.json
  data/exports/oil-markets-latest.csv
  data/exports/oil-markets-latest.json
  data/exports/oil-markets-history.csv
  data/exports/oil-markets-history.json
"""

import sqlite3
import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "data" / "oil_markets.db"
EXPORT_DIR = SCRIPT_DIR / "data" / "exports"
DAILY_DIR = EXPORT_DIR / "daily"

# Ensure export directories exist
DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_daily_close_readings(conn):
    """Get one reading per calendar day (the last reading of each day).
    Uses the last reading's values as the daily 'close'."""
    rows = conn.execute("""
        SELECT date(timestamp) as date,
               MAX(timestamp) as timestamp,
               value as index_value,
               wti_price,
               brent_price
        FROM readings
        GROUP BY date(timestamp)
        ORDER BY date ASC
    """).fetchall()
    return [dict(r) for r in rows]


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


CSV_FIELDS = ["date", "index_value", "wti_price", "brent_price"]


def generate_daily_snapshot(conn, date_str=None):
    """Generate CSV/JSON for a specific date (defaults to today)."""
    if date_str is None:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Get the last reading for this date
    reading = conn.execute("""
        SELECT MAX(timestamp) as timestamp,
               value as index_value,
               wti_price,
               brent_price
        FROM readings WHERE date(timestamp) = ?
    """, (date_str,)).fetchone()

    if not reading or reading["index_value"] is None:
        print(f"  No data for {date_str}, skipping daily snapshot")
        return

    row = {
        "date": date_str,
        "index_value": round(reading["index_value"], 2),
        "wti_price": round(reading["wti_price"], 2) if reading["wti_price"] else "",
        "brent_price": round(reading["brent_price"], 2) if reading["brent_price"] else "",
    }

    # Daily CSV — one row
    csv_path = DAILY_DIR / f"{date_str}.csv"
    write_csv(csv_path, [row], CSV_FIELDS)

    # Daily JSON
    json_data = {
        "date": date_str,
        "timestamp": reading["timestamp"],
        "index_value": round(reading["index_value"], 2),
        "wti_price": round(reading["wti_price"], 2) if reading["wti_price"] else None,
        "brent_price": round(reading["brent_price"], 2) if reading["brent_price"] else None,
    }
    json_path = DAILY_DIR / f"{date_str}.json"
    write_json(json_path, json_data)

    return json_data


def generate_latest(conn):
    """Generate latest.csv and latest.json (always current day)."""
    readings = get_daily_close_readings(conn)
    if not readings:
        print("  No readings found")
        return

    latest = readings[-1]
    row = {
        "date": latest["date"],
        "index_value": round(latest["index_value"], 2),
        "wti_price": round(latest["wti_price"], 2) if latest["wti_price"] else "",
        "brent_price": round(latest["brent_price"], 2) if latest["brent_price"] else "",
    }

    write_csv(
        EXPORT_DIR / "oil-markets-latest.csv",
        [row],
        CSV_FIELDS,
    )

    write_json(EXPORT_DIR / "oil-markets-latest.json", {
        "export_date": datetime.utcnow().isoformat(),
        "date": latest["date"],
        "timestamp": latest["timestamp"],
        "index_value": round(latest["index_value"], 2),
        "wti_price": round(latest["wti_price"], 2) if latest["wti_price"] else None,
        "brent_price": round(latest["brent_price"], 2) if latest["brent_price"] else None,
    })


def generate_history(conn):
    """Generate full history CSV/JSON — one row per calendar day."""
    readings = get_daily_close_readings(conn)

    # Build rows for CSV
    csv_rows = []
    for r in readings:
        csv_rows.append({
            "date": r["date"],
            "index_value": round(r["index_value"], 2),
            "wti_price": round(r["wti_price"], 2) if r["wti_price"] else "",
            "brent_price": round(r["brent_price"], 2) if r["brent_price"] else "",
        })

    # History CSV
    write_csv(
        EXPORT_DIR / "oil-markets-history.csv",
        csv_rows,
        CSV_FIELDS,
    )

    # History JSON
    json_data = []
    for r in readings:
        json_data.append({
            "date": r["date"],
            "timestamp": r["timestamp"],
            "index_value": round(r["index_value"], 2),
            "wti_price": round(r["wti_price"], 2) if r["wti_price"] else None,
            "brent_price": round(r["brent_price"], 2) if r["brent_price"] else None,
        })

    write_json(EXPORT_DIR / "oil-markets-history.json", {
        "export_date": datetime.utcnow().isoformat(),
        "record_count": len(json_data),
        "data": json_data,
    })


def main():
    print(f"[{datetime.utcnow().isoformat()}] Generating Oil Markets Index exports...")
    print(f"  DB: {DB_PATH}")
    print(f"  Export dir: {EXPORT_DIR}")
    print()

    conn = get_db()

    try:
        # 1. Today's daily snapshot
        today = datetime.utcnow().strftime("%Y-%m-%d")
        print(f"1. Daily snapshot for {today}:")
        generate_daily_snapshot(conn, today)
        print()

        # 2. Latest files
        print("2. Latest files:")
        generate_latest(conn)
        print()

        # 3. Full history
        print("3. Full history:")
        generate_history(conn)
        print()

        print("Export generation complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
