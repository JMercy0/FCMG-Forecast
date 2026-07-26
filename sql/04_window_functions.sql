-- ============================================================
-- File: window_functions.sql
-- Project: FMCG Global Demand Planning & Forecasting
-- Description: Window Function Analysis
-- Database: PostgreSQL
-- ============================================================


-- ============================================================
-- Window Function 1
-- Rank Products by Total Revenue
-- ============================================================

SELECT
    sku_name,
    SUM(net_sales) AS revenue,
    RANK() OVER (
        ORDER BY SUM(net_sales) DESC
    ) AS revenue_rank
FROM fmcg_sales
GROUP BY sku_name
ORDER BY revenue_rank;


-- ============================================================
-- Window Function 2
-- Dense Rank Products by Revenue
-- ============================================================

SELECT
    sku_name,
    SUM(net_sales) AS revenue,
    DENSE_RANK() OVER (
        ORDER BY SUM(net_sales) DESC
    ) AS dense_rank
FROM fmcg_sales
GROUP BY sku_name
ORDER BY dense_rank;


-- ============================================================
-- Window Function 3
-- Running (Cumulative) Revenue Over Time
-- ============================================================

SELECT
    date,
    SUM(net_sales) AS daily_revenue,
    SUM(SUM(net_sales)) OVER (
        ORDER BY date
    ) AS cumulative_revenue
FROM fmcg_sales
GROUP BY date
ORDER BY date;


-- ============================================================
-- Window Function 4
-- Revenue Contribution by Country
-- ============================================================

SELECT
    country,
    SUM(net_sales) AS revenue,
    ROUND(
        (
            100.0 * SUM(net_sales)
            / SUM(SUM(net_sales)) OVER ()
        )::NUMERIC,
        2
    ) AS revenue_percent
FROM fmcg_sales
GROUP BY country
ORDER BY revenue_percent DESC;