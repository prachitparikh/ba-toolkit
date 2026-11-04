"""Tests for the Northstar Systems revenue reconciliation.

Run from this folder:  pytest
"""

import filecmp
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import generate_data  # noqa: E402
import run  # noqa: E402

EXPECTED = {
    "finance": 1_236_200.00,
    "dashboard": 1_284_500.00,
    "cancelled": 9_600.00,
    "timezone": 4_200.00,
    "fanout": 41_900.00,
    "orphans": -7_400.00,
}
COMPONENTS = ["cancelled", "timezone", "fanout", "orphans"]


def cents(x: float) -> int:
    return round(x * 100)


@pytest.fixture(scope="module")
def conn():
    connection = run.load_database()
    yield connection
    connection.close()


@pytest.fixture(scope="module")
def result(conn):
    return run.reconcile(conn)


@pytest.fixture(scope="module")
def daily(conn):
    return run.daily_rows(conn)


def test_finance_revenue(result):
    assert cents(result["finance"]) == cents(EXPECTED["finance"])


def test_dashboard_revenue(result):
    assert cents(result["dashboard"]) == cents(EXPECTED["dashboard"])


@pytest.mark.parametrize("component", COMPONENTS)
def test_bridge_component(result, component):
    assert cents(result[component]) == cents(EXPECTED[component])


def test_bridge_balances_to_the_cent(result):
    explained = result["finance"] + sum(result[c] for c in COMPONENTS)
    assert cents(explained) == cents(result["dashboard"])
    assert result["check"]["result"] == "BALANCED"
    assert result["check"]["unexplained"] == 0


def test_bridge_rows_end_on_dashboard(result):
    rows = run.bridge_rows(result)
    assert [r["step_order"] for r in rows] == [0, 1, 2, 3, 4, 5]
    assert cents(rows[-2]["running_total"]) == cents(EXPECTED["dashboard"])


def test_daily_covers_every_october_day(daily):
    assert len(daily) == 31
    assert daily[0]["date"] == "2026-10-01"
    assert daily[-1]["date"] == "2026-10-31"


def test_daily_totals_match_monthly(daily, result):
    assert cents(sum(r["finance_revenue"] for r in daily)) == cents(result["finance"])
    assert cents(sum(r["dashboard_revenue"] for r in daily)) == cents(result["dashboard"])
    for c in COMPONENTS:
        assert cents(sum(r[c] for r in daily)) == cents(result[c]), c


def test_each_day_balances(daily):
    for r in daily:
        explained = r["finance_revenue"] + sum(r[c] for c in COMPONENTS)
        assert cents(explained) == cents(r["dashboard_revenue"]), r["date"]
        assert cents(r["gap"]) == cents(r["dashboard_revenue"] - r["finance_revenue"]), r["date"]


def test_problems_are_spread_across_days(daily):
    for c in ["cancelled", "fanout", "orphans"]:
        days_hit = [r["date"] for r in daily if r[c] != 0]
        assert len(days_hit) >= 4, c
    tz_days = [r["date"] for r in daily if r["timezone"] != 0]
    assert tz_days == ["2026-10-01", "2026-10-31"]


def test_generator_is_deterministic(tmp_path):
    generate_data.main(tmp_path)
    for name in ["customers.csv", "orders.csv", "order_promotions.csv"]:
        assert filecmp.cmp(tmp_path / name, HERE / "data" / name, shallow=False), name
