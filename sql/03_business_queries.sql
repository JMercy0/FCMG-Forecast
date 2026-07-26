-- ==========================================
-- Business Query 1
-- Total Revenue by Country
-- ==========================================

SELECT
    country,
    SUM(net_sales) AS total_revenue
FROM fmcg_sales
GROUP BY country
ORDER BY total_revenue DESC;


SELECT
    channel,
    SUM(net_sales) AS revenue
FROM fmcg_sales
GROUP BY channel
ORDER BY revenue DESC;

SELECT
    sku_name,
    SUM(net_sales) AS revenue
FROM fmcg_sales
GROUP BY sku_name
ORDER BY revenue DESC
LIMIT 20;

SELECT
    sku_name,
    ROUND(AVG(unit_price),2) AS average_price
FROM fmcg_sales
GROUP BY sku_name
ORDER BY average_price DESC;


SELECT

DATE_TRUNC('month',date) AS month,

SUM(net_sales) AS revenue

FROM fmcg_sales

GROUP BY month

ORDER BY month;