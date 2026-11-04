"""Run the Northstar Systems revenue reconciliation.

Loads data/*.csv into an in-memory SQLite database, runs reconcile.sql,
prints the bridge from finance revenue to dashboard revenue, and writes:

    output/bridge.csv  step_order, step, amount, running_total
    output/daily.csv   date, finance_revenue, dashboard_revenue, gap,
                       cancelled, timezone, fanout, orphans

Standard library only.

Usage:
    python run.py
"""

import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
OUTPUT_DIR = HERE / "output"
SQL_FILE = HERE / "reconcile.sql"

TABLES = {
    "customers": "customer_id TEXT PRIMARY KEY, customer_name TEXT, region TEXT",
    "orders": ("order_id TEXT PRIMARY KEY, customer_id TEXT, order_ts_utc TEXT, "
               "status TEXT, amount REAL"),
    "order_promotions": "promo_id TEXT PRIMARY KEY, order_id TEXT, promo_code TEXT",
}

BRIDGE_STEPS = [
    ("cancelled", "Cancelled orders still counted on the dashboard"),
    ("timezone", "Time-zone cutoff (dashboard uses UTC, finance uses US Eastern)"),
    ("fanout", "JOIN fan-out on order_promotions (double counting)"),
    ("orphans", "Orphan orders dropped by the INNER JOIN to customers"),
]

DAILY_COLUMNS = ["date", "finance_revenue", "dashboard_revenue", "gap",
                 "cancelled", "timezone", "fanout", "orphans"]


def load_database(data_dir: Path = DATA_DIR) -> sqlite3.Connection:
    """Create an in-memory database and load the three CSVs into it."""
    conn = sqlite3.connect(":memory:")
    for table, columns in TABLES.items():
        conn.execute(f"CREATE TABLE {table} ({columns})")
        with (data_dir / f"{table}.csv").open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            names = reader.fieldnames
            placeholders = ", ".join("?" for _ in names)
            conn.executemany(
                f"INSERT INTO {table} ({', '.join(names)}) VALUES ({placeholders})",
                ([row[n] for n in names] for row in reader),
            )
    conn.executescript(SQL_FILE.read_text(encoding="utf-8"))
    return conn


def scalar(conn: sqlite3.Connection, view: str) -> float:
    return round(conn.execute(f"SELECT amount FROM {view}").fetchone()[0], 2)


def reconcile(conn: sqlite3.Connection) -> dict:
    """Return finance, dashboard, each bridge component and the check row."""
    check_cursor = conn.execute("SELECT * FROM bridge_check")
    check = dict(zip([c[0] for c in check_cursor.description], check_cursor.fetchone()))
    return {
        "finance": scalar(conn, "finance_revenue"),
        "dashboard": scalar(conn, "dashboard_revenue"),
        "cancelled": scalar(conn, "bridge_cancelled"),
        "timezone": scalar(conn, "bridge_timezone"),
        "fanout": scalar(conn, "bridge_fanout"),
        "orphans": scalar(conn, "bridge_orphans"),
        "check": check,
    }


def bridge_rows(result: dict) -> list[dict]:
    """Finance first, then each component with a running total, then the dashboard."""
    rows = [{"step_order": 0, "step": "Finance ledger revenue (completed orders, US Eastern date)",
             "amount": result["finance"], "running_total": result["finance"]}]
    running = result["finance"]
    for i, (key, label) in enumerate(BRIDGE_STEPS, start=1):
        running = round(running + result[key], 2)
        rows.append({"step_order": i, "step": label,
                     "amount": result[key], "running_total": running})
    rows.append({"step_order": len(BRIDGE_STEPS) + 1, "step": "Revenue dashboard",
                 "amount": result["dashboard"], "running_total": result["dashboard"]})
    return rows


def daily_rows(conn: sqlite3.Connection) -> list[dict]:
    cursor = conn.execute(f"SELECT {', '.join(DAILY_COLUMNS)} FROM daily_reconciliation")
    return [dict(zip(DAILY_COLUMNS, row)) for row in cursor]


def money(x: float) -> str:
    return f"{x:.2f}"


def write_outputs(bridge: list[dict], daily: list[dict], out_dir: Path = OUTPUT_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "bridge.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["step_order", "step", "amount", "running_total"])
        for r in bridge:
            writer.writerow([r["step_order"], r["step"], money(r["amount"]),
                             money(r["running_total"])])
    with (out_dir / "daily.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(DAILY_COLUMNS)
        for r in daily:
            writer.writerow([r["date"]] + [money(r[c]) for c in DAILY_COLUMNS[1:]])


def print_bridge(bridge: list[dict], check: dict) -> None:
    print("Northstar Systems (fictional) revenue reconciliation, October 2026\n")
    print(f"{'Step':<66}{'Amount':>15}{'Running total':>16}")
    print("-" * 97)
    for r in bridge:
        amount = f"{r['amount']:,.2f}"
        if 0 < r["step_order"] <= len(BRIDGE_STEPS):
            amount = f"{r['amount']:+,.2f}"
        print(f"{r['step']:<66}{amount:>15}{r['running_total']:>16,.2f}")
    print("-" * 97)
    gap = bridge[-1]["amount"] - bridge[0]["amount"]
    print(f"Gap to explain: {gap:,.2f}")
    print(f"Check: {check['result']} (unexplained {check['unexplained']:.2f})")


def main() -> None:
    conn = load_database()
    result = reconcile(conn)
    bridge = bridge_rows(result)
    daily = daily_rows(conn)
    write_outputs(bridge, daily)
    print_bridge(bridge, result["check"])
    print(f"\nWrote {OUTPUT_DIR / 'bridge.csv'} and {OUTPUT_DIR / 'daily.csv'}")


if __name__ == "__main__":
    main()
