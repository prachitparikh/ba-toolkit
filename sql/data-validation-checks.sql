-- Data validation checks before UAT sign-off
-- From the BA Toolkit by Prachit Parikh: https://github.com/prachitparikh/ba-toolkit
-- Background article: https://dev.to/prachitparikh/7-sql-checks-i-run-before-uat-sign-off-with-queries-you-can-copy-38h5
-- Table and column names are examples. Replace them with your own. Syntax is ANSI-style;
-- DATE_TRUNC works in PostgreSQL, Snowflake and Redshift (use FORMAT/DATEFROMPARTS in SQL Server).

-- 1. Row counts: did everything arrive?
SELECT 'source' AS side, COUNT(*) AS row_count
FROM staging.orders
WHERE load_date = '2026-10-30'
UNION ALL
SELECT 'target', COUNT(*)
FROM dw.fact_orders
WHERE load_date = '2026-10-30';

-- 2. Totals that should tie out, by month
SELECT DATE_TRUNC('month', order_date) AS month,
       SUM(order_amount) AS total_amount
FROM dw.fact_orders
GROUP BY 1
ORDER BY 1;

-- 3. Duplicates on the business key
SELECT order_number, COUNT(*) AS copies
FROM dw.fact_orders
GROUP BY order_number
HAVING COUNT(*) > 1
ORDER BY copies DESC;

-- 4. Orphans: records pointing at nothing
SELECT o.order_number, o.customer_id
FROM dw.fact_orders o
LEFT JOIN dw.dim_customer c
       ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;

-- 5. Nulls in fields the business marked as mandatory
SELECT COUNT(*) AS total_rows,
       SUM(CASE WHEN region IS NULL THEN 1 ELSE 0 END)       AS missing_region,
       SUM(CASE WHEN product_code IS NULL THEN 1 ELSE 0 END) AS missing_product,
       SUM(CASE WHEN order_amount IS NULL THEN 1 ELSE 0 END) AS missing_amount
FROM dw.fact_orders;

-- 6. Values outside the allowed list
SELECT status, COUNT(*) AS rows_with_status
FROM dw.fact_orders
WHERE status NOT IN ('Open', 'Shipped', 'Cancelled', 'Returned')
   OR status IS NULL
GROUP BY status;

-- 7. Trace real records end to end (pick 5 the business knows well)
SELECT o.order_number, o.order_date, o.status, o.order_amount,
       c.customer_name, c.region
FROM dw.fact_orders o
JOIN dw.dim_customer c ON c.customer_id = o.customer_id
WHERE o.order_number IN ('SO-10001', 'SO-10457', 'SO-11020', 'SO-11234', 'SO-11999');

-- Log every result: check, query file, expected, actual, pass/fail, defect ID.
