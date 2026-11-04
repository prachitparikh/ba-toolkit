-- Revenue reconciliation: why the dashboard and the finance ledger disagree
-- From the BA Toolkit by Prachit Parikh: https://github.com/prachitparikh/ba-toolkit
-- Video walkthrough: https://www.youtube.com/watch?v=SG-6rtZeizg
--
-- Client: Northstar Systems (fictional). Period: October 2026. Dialect: SQLite.
-- Expects three tables loaded from data/: customers, orders, order_promotions.
-- run.py loads them for you. In the sqlite3 shell, import the CSVs, then:
--   .read reconcile.sql
--   SELECT * FROM bridge_check;
--
-- Every result is a view, so you can read this file top to bottom and query
-- any step on its own.

DROP VIEW IF EXISTS order_facts;
DROP VIEW IF EXISTS finance_revenue;
DROP VIEW IF EXISTS dashboard_revenue;
DROP VIEW IF EXISTS bridge_cancelled;
DROP VIEW IF EXISTS bridge_timezone;
DROP VIEW IF EXISTS bridge_fanout;
DROP VIEW IF EXISTS bridge_orphans;
DROP VIEW IF EXISTS bridge_check;
DROP VIEW IF EXISTS daily_reconciliation;


-- Helper: one row per order with the facts every other query needs.
--   utc_date      the calendar date in UTC (what the dashboard groups by)
--   et_date       the calendar date in US Eastern (what finance books by).
--                 Eastern is UTC-4 until 2:00 am on Nov 1 2026, then UTC-5.
--                 That rule only covers this data window. On a real project,
--                 use your warehouse's time-zone function instead.
--   promo_rows    how many rows this order has in order_promotions
--   has_customer  1 if the customer_id exists in customers, otherwise 0
CREATE VIEW order_facts AS
SELECT o.order_id,
       o.customer_id,
       o.status,
       o.amount,
       o.order_ts_utc,
       date(o.order_ts_utc) AS utc_date,
       date(o.order_ts_utc,
            CASE WHEN o.order_ts_utc < '2026-11-01T06:00:00Z'
                 THEN '-4 hours' ELSE '-5 hours' END) AS et_date,
       (SELECT COUNT(*) FROM order_promotions p
         WHERE p.order_id = o.order_id) AS promo_rows,
       EXISTS (SELECT 1 FROM customers c
                WHERE c.customer_id = o.customer_id) AS has_customer
FROM orders o;


-- (a) Finance ledger revenue: the number finance reports.
-- Rule: completed orders only, each order counted once, booked on its
-- US Eastern date. The customer table is not involved, so an order with a
-- missing customer record still counts. Its revenue is real.
CREATE VIEW finance_revenue AS
SELECT SUM(amount) AS amount,
       COUNT(*)    AS orders
FROM order_facts
WHERE status = 'completed'
  AND et_date BETWEEN '2026-10-01' AND '2026-10-31';


-- (b) Revenue dashboard: the query behind the dashboard tile, bugs included.
-- Written the way it looks in the dashboard tool. Read it slowly:
--   * no status filter, so cancelled orders are counted
--   * date(order_ts_utc) groups by the UTC date, not the Eastern date
--   * LEFT JOIN to order_promotions repeats an order once per promotion row,
--     and SUM(o.amount) adds the same order amount again for each repeat
--   * INNER JOIN to customers quietly drops orders whose customer is missing
CREATE VIEW dashboard_revenue AS
SELECT SUM(o.amount) AS amount,
       COUNT(*)      AS joined_rows
FROM orders o
JOIN customers c
  ON c.customer_id = o.customer_id
LEFT JOIN order_promotions p
  ON p.order_id = o.order_id
WHERE date(o.order_ts_utc) BETWEEN '2026-10-01' AND '2026-10-31';


-- (c) The bridge. Each component is its own query, so each one can be
-- shown to the dashboard owner with the orders behind it.

-- (c1) Cancelled orders still counted on the dashboard. (Adds to the dashboard.)
-- Cancelled orders in October that finance leaves out.
CREATE VIEW bridge_cancelled AS
SELECT COALESCE(SUM(amount), 0) AS amount,
       COUNT(*)                 AS orders
FROM order_facts
WHERE status = 'cancelled'
  AND et_date BETWEEN '2026-10-01' AND '2026-10-31';

-- (c2) Time-zone cutoff. (Usually small, can go either way.)
-- Revenue in October by UTC date minus revenue in October by Eastern date.
-- Evening orders on Sep 30 Eastern are already Oct 1 in UTC, so the
-- dashboard picks them up. Evening orders on Oct 31 Eastern are Nov 1 in UTC,
-- so the dashboard misses them. The net of the two is this component.
CREATE VIEW bridge_timezone AS
SELECT COALESCE(SUM(CASE WHEN utc_date BETWEEN '2026-10-01' AND '2026-10-31'
                         THEN amount ELSE 0 END), 0)
     - COALESCE(SUM(CASE WHEN et_date  BETWEEN '2026-10-01' AND '2026-10-31'
                         THEN amount ELSE 0 END), 0) AS amount,
       SUM(CASE WHEN (utc_date BETWEEN '2026-10-01' AND '2026-10-31')
                  <> (et_date  BETWEEN '2026-10-01' AND '2026-10-31')
                THEN 1 ELSE 0 END) AS orders
FROM order_facts;

-- (c3) JOIN fan-out. (Adds to the dashboard.)
-- An order with 3 promotion rows shows up 3 times after the join, so its
-- amount is counted 2 extra times. Only orders the dashboard keeps (customer
-- exists, October by UTC date) can be double counted.
CREATE VIEW bridge_fanout AS
SELECT COALESCE(SUM(amount * (promo_rows - 1)), 0) AS amount,
       COUNT(*)                                    AS orders
FROM order_facts
WHERE promo_rows > 1
  AND has_customer = 1
  AND utc_date BETWEEN '2026-10-01' AND '2026-10-31';

-- (c4) Orphan orders. (Takes away from the dashboard, so the sign is negative.)
-- Orders in the dashboard's date range whose customer_id has no match in
-- customers. The INNER JOIN drops them without any warning.
CREATE VIEW bridge_orphans AS
SELECT -COALESCE(SUM(amount), 0) AS amount,
       COUNT(*)                  AS orders
FROM order_facts
WHERE has_customer = 0
  AND utc_date BETWEEN '2026-10-01' AND '2026-10-31';


-- (d) The check. Finance plus every bridge component must land exactly on
-- the dashboard. If "unexplained" is anything but 0.00, there is a cause we
-- have not found yet and the reconciliation is not done.
CREATE VIEW bridge_check AS
SELECT f.amount                                   AS finance,
       c1.amount                                  AS cancelled,
       c2.amount                                  AS timezone,
       c3.amount                                  AS fanout,
       c4.amount                                  AS orphans,
       f.amount + c1.amount + c2.amount + c3.amount + c4.amount
                                                  AS finance_plus_bridge,
       d.amount                                   AS dashboard,
       ROUND(d.amount - (f.amount + c1.amount + c2.amount + c3.amount + c4.amount), 2)
                                                  AS unexplained,
       CASE WHEN ROUND(d.amount - (f.amount + c1.amount + c2.amount
                                   + c3.amount + c4.amount), 2) = 0
            THEN 'BALANCED' ELSE 'NOT BALANCED' END AS result
FROM finance_revenue f, dashboard_revenue d,
     bridge_cancelled c1, bridge_timezone c2, bridge_fanout c3, bridge_orphans c4;


-- (e) Day by day. Same rules as above, one row per day in October.
-- Finance is booked on the Eastern date and the dashboard on the UTC date.
-- Each component sits on the day it affects, so on every row:
--   finance_revenue + cancelled + timezone + fanout + orphans = dashboard_revenue
CREATE VIEW daily_reconciliation AS
WITH RECURSIVE days(day) AS (
    SELECT '2026-10-01'
    UNION ALL
    SELECT date(day, '+1 day') FROM days WHERE day < '2026-10-31'
),
finance AS (
    SELECT et_date AS day, SUM(amount) AS amount
    FROM order_facts WHERE status = 'completed' GROUP BY et_date
),
dashboard AS (
    -- The same buggy dashboard query, grouped by its UTC date
    SELECT date(o.order_ts_utc) AS day, SUM(o.amount) AS amount
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    LEFT JOIN order_promotions p ON p.order_id = o.order_id
    GROUP BY date(o.order_ts_utc)
),
cancelled AS (
    SELECT et_date AS day, SUM(amount) AS amount
    FROM order_facts WHERE status = 'cancelled' GROUP BY et_date
),
by_utc AS (
    SELECT utc_date AS day, SUM(amount) AS amount FROM order_facts GROUP BY utc_date
),
by_et AS (
    SELECT et_date AS day, SUM(amount) AS amount FROM order_facts GROUP BY et_date
),
fanout AS (
    SELECT utc_date AS day, SUM(amount * (promo_rows - 1)) AS amount
    FROM order_facts WHERE promo_rows > 1 AND has_customer = 1 GROUP BY utc_date
),
orphans AS (
    SELECT utc_date AS day, -SUM(amount) AS amount
    FROM order_facts WHERE has_customer = 0 GROUP BY utc_date
)
SELECT days.day                                              AS date,
       COALESCE(finance.amount, 0)                           AS finance_revenue,
       COALESCE(dashboard.amount, 0)                         AS dashboard_revenue,
       COALESCE(dashboard.amount, 0) - COALESCE(finance.amount, 0) AS gap,
       COALESCE(cancelled.amount, 0)                         AS cancelled,
       COALESCE(by_utc.amount, 0) - COALESCE(by_et.amount, 0) AS timezone,
       COALESCE(fanout.amount, 0)                            AS fanout,
       COALESCE(orphans.amount, 0)                           AS orphans
FROM days
LEFT JOIN finance   ON finance.day   = days.day
LEFT JOIN dashboard ON dashboard.day = days.day
LEFT JOIN cancelled ON cancelled.day = days.day
LEFT JOIN by_utc    ON by_utc.day    = days.day
LEFT JOIN by_et     ON by_et.day     = days.day
LEFT JOIN fanout    ON fanout.day    = days.day
LEFT JOIN orphans   ON orphans.day   = days.day
ORDER BY days.day;
