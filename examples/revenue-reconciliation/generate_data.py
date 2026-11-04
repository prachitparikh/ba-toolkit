"""Generate the sample data for the Northstar Systems revenue reconciliation.

Northstar Systems is a fictional client. Every row here is generated, and four
data problems are planted on purpose so the SQL in reconcile.sql can find them:

  1. Cancelled orders that the dashboard still counts        +9,600
  2. Time-zone cutoff (dashboard uses UTC, finance US Eastern) +4,200
  3. JOIN fan-out on order_promotions (double counting)       +41,900
  4. Orphan orders whose customer record is missing           -7,400

Finance ledger revenue for October 2026 comes out at 1,236,200 and the
dashboard at 1,284,500. The planted orders are listed in plain sight below so
you can see exactly what goes in.

Standard library only. The seed is fixed, so every run writes the same files.

Usage:
    python generate_data.py            # writes ./data/*.csv
    python generate_data.py some/dir   # writes to another folder
"""

import csv
import datetime as dt
import random
import sys
from pathlib import Path

SEED = 20261031
HERE = Path(__file__).resolve().parent

# Targets from the video. All amounts are whole dollars.
FINANCE_TARGET = 1_236_200

# US Eastern is UTC-4 (EDT) until 2:00 am on Sunday Nov 1 2026, then UTC-5 (EST).
EDT = dt.timezone(dt.timedelta(hours=-4))
EST = dt.timezone(dt.timedelta(hours=-5))
DST_END_LOCAL = dt.datetime(2026, 11, 1, 2, 0)

# ---------------------------------------------------------------------------
# Planted problems. (October day, Eastern hour, Eastern minute, amount, ...)
# All of them sit inside business hours so their Eastern date and UTC date
# are the same day. Only the time-zone orders are placed in the evening.
# ---------------------------------------------------------------------------

# 1. Cancelled orders. Finance excludes them; the dashboard has no status filter.
CANCELLED = [  # (day, hour, minute, amount)  total 9,600
    (3, 10, 12, 1_200),
    (8, 14, 47, 2_100),
    (14, 9, 31, 900),
    (19, 16, 5, 1_800),
    (23, 11, 58, 2_400),
    (28, 13, 20, 1_200),
]

# 2. Time-zone cutoff. Evening orders in US Eastern land on the next UTC date.
#    Sep 30 evening (Eastern) shows up as Oct 1 on the dashboard:  +10,500
#    Oct 31 evening (Eastern) shows up as Nov 1 on the dashboard:   -6,300
TZ_SEP30_EVENING = [  # (hour, minute, amount)
    (20, 41, 3_100),
    (21, 56, 2_800),
    (23, 12, 4_600),
]
TZ_OCT31_EVENING = [
    (20, 27, 2_700),
    (22, 49, 3_600),
]

# 3. JOIN fan-out. Completed orders with more than one promotion row.
#    The dashboard repeats the order amount once per promotion row,
#    so each order adds amount x (rows - 1).  Total extra: 41,900
FANOUT = [  # (day, hour, minute, amount, promotion_rows)
    (2, 11, 15, 3_200, 2),
    (5, 15, 40, 2_500, 3),
    (7, 9, 52, 4_100, 2),
    (9, 13, 8, 1_800, 2),
    (13, 10, 26, 2_900, 3),
    (16, 17, 33, 3_600, 2),
    (20, 12, 4, 2_200, 2),
    (22, 14, 19, 1_500, 3),
    (26, 10, 45, 4_800, 2),
    (27, 16, 11, 2_700, 2),
    (29, 9, 37, 1_900, 4),
]

# 4. Orphan orders. Completed and real revenue, but the customer_id does not
#    exist in customers.csv, so the dashboard's INNER JOIN drops them.
ORPHANS = [  # (day, hour, minute, amount, customer_id)  total 7,400
    (6, 10, 3, 1_600, "C-1093"),
    (12, 15, 22, 2_200, "C-1097"),
    (17, 11, 48, 900, "C-1102"),
    (21, 13, 36, 1_300, "C-1104"),
    (30, 9, 14, 1_400, "C-1111"),
]

PROMO_CODES = ["FALL10", "VOLUME5", "LOYALTY3", "FREESHIP", "BUNDLE15", "RENEW8"]
REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]
NAME_FIRST = ["Harbor", "Summit", "Cedar", "Granite", "Bluewater", "Ironwood",
              "Lakeshore", "Redfield", "Silverline", "Oakmont", "Brightpath",
              "Westbrook", "Pinecrest", "Copperhill", "Riverside"]
NAME_SECOND = ["Tooling", "Freight", "Fabrication", "Supply", "Controls",
               "Packaging", "Components", "Logistics", "Machining", "Plastics"]


def to_utc(local: dt.datetime) -> dt.datetime:
    """Turn a naive US Eastern wall-clock time into UTC."""
    tz = EDT if local < DST_END_LOCAL else EST
    return local.replace(tzinfo=tz).astimezone(dt.timezone.utc)


def iso_utc(local: dt.datetime) -> str:
    return to_utc(local).strftime("%Y-%m-%dT%H:%M:%SZ")


def business_time(rng: random.Random, day: dt.date) -> dt.datetime:
    """A random Eastern time between 8:00 am and 6:59 pm."""
    return dt.datetime(day.year, day.month, day.day,
                       rng.randint(8, 18), rng.randint(0, 59), rng.randint(0, 59))


def make_customers(rng: random.Random) -> list[dict]:
    names = [f"{a} {b}" for a in NAME_FIRST for b in NAME_SECOND]
    rng.shuffle(names)
    return [
        {"customer_id": f"C-{1001 + i}", "customer_name": names[i],
         "region": rng.choice(REGIONS)}
        for i in range(90)
    ]


def spread_to_target(rng: random.Random, amounts: list[int], target: int) -> None:
    """Nudge amounts in $5 steps until they add up to target exactly."""
    diff = target - sum(amounts)
    assert diff % 5 == 0
    while diff != 0:
        i = rng.randrange(len(amounts))
        step = min(abs(diff), 5 * rng.randint(1, 20))
        new = amounts[i] + step if diff > 0 else amounts[i] - step
        if 150 <= new <= 6_000:
            amounts[i] = new
            diff += -step if diff > 0 else step


def build(rng: random.Random):
    customers = make_customers(rng)
    customer_ids = [c["customer_id"] for c in customers]
    orders = []  # dicts with local_ts, customer_id, status, amount, promo_rows

    def add(local_ts, amount, status="completed", customer_id=None, promo_rows=None):
        if promo_rows is None:
            promo_rows = 1 if rng.random() < 0.3 else 0
        orders.append({
            "local_ts": local_ts,
            "customer_id": customer_id or rng.choice(customer_ids),
            "status": status,
            "amount": amount,
            "promo_rows": promo_rows,
        })

    # Normal October orders: busier on weekdays, quieter on weekends.
    october = [dt.date(2026, 10, d) for d in range(1, 32)]
    slots = []
    for day in october:
        count = rng.randint(17, 24) if day.weekday() < 5 else rng.randint(5, 9)
        slots += [day] * count
    amounts = [5 * rng.randint(60, 800) for _ in slots]  # $300 to $4,000

    planted_completed_in_october = (
        sum(a for _, _, _, a, _ in FANOUT)
        + sum(a for _, _, _, a, _ in ORPHANS)
        + sum(a for _, _, a in TZ_OCT31_EVENING)
    )
    spread_to_target(rng, amounts, FINANCE_TARGET - planted_completed_in_october)
    for day, amount in zip(slots, amounts):
        add(business_time(rng, day), amount)

    # Normal orders just outside the month, so the boundaries have real traffic.
    for day, count in ((dt.date(2026, 9, 30), 18), (dt.date(2026, 11, 1), 6)):
        for _ in range(count):
            add(business_time(rng, day), 5 * rng.randint(60, 800))

    # Planted problems.
    for d, h, m, amount in CANCELLED:
        add(dt.datetime(2026, 10, d, h, m, rng.randint(0, 59)), amount,
            status="cancelled", promo_rows=rng.choice([0, 1]))
    for h, m, amount in TZ_SEP30_EVENING:
        add(dt.datetime(2026, 9, 30, h, m, rng.randint(0, 59)), amount,
            promo_rows=rng.choice([0, 1]))
    for h, m, amount in TZ_OCT31_EVENING:
        add(dt.datetime(2026, 10, 31, h, m, rng.randint(0, 59)), amount,
            promo_rows=rng.choice([0, 1]))
    for d, h, m, amount, rows in FANOUT:
        add(dt.datetime(2026, 10, d, h, m, rng.randint(0, 59)), amount, promo_rows=rows)
    for d, h, m, amount, cust in ORPHANS:
        add(dt.datetime(2026, 10, d, h, m, rng.randint(0, 59)), amount,
            customer_id=cust, promo_rows=rng.choice([0, 1]))

    # Order IDs follow time, so planted orders sit among normal ones.
    orders.sort(key=lambda o: (o["local_ts"], o["customer_id"], o["amount"]))
    promotions = []
    for n, o in enumerate(orders, start=1):
        o["order_id"] = f"NS-{50000 + n}"
        for code in rng.sample(PROMO_CODES, o["promo_rows"]):
            promotions.append({"promo_id": f"PR-{len(promotions) + 1:05d}",
                               "order_id": o["order_id"], "promo_code": code})
    return customers, orders, promotions


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(out_dir: Path) -> None:
    rng = random.Random(SEED)
    customers, orders, promotions = build(rng)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_csv(out_dir / "customers.csv", ["customer_id", "customer_name", "region"], customers)
    write_csv(
        out_dir / "orders.csv",
        ["order_id", "customer_id", "order_ts_utc", "status", "amount"],
        [{"order_id": o["order_id"], "customer_id": o["customer_id"],
          "order_ts_utc": iso_utc(o["local_ts"]), "status": o["status"],
          "amount": f"{o['amount']:.2f}"} for o in orders],
    )
    write_csv(out_dir / "order_promotions.csv", ["promo_id", "order_id", "promo_code"], promotions)
    print(f"Wrote {len(customers)} customers, {len(orders)} orders and "
          f"{len(promotions)} promotion rows to {out_dir}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "data")
