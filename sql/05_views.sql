CREATE OR REPLACE VIEW vw_monthly_sales AS

SELECT

    year,

    month,

    ROUND(SUM(net_sales)::numeric,2) AS monthly_sales,

    SUM(units_sold) AS units_sold

FROM fmcg_sales

GROUP BY

    year,

    month

ORDER BY

    year,

    month;


##
CREATE OR REPLACE VIEW vw_country_sales AS

SELECT

    country,

    ROUND(SUM(net_sales)::numeric,2) AS revenue,

    SUM(units_sold) AS units

FROM fmcg_sales

GROUP BY country

ORDER BY revenue DESC;

##
CREATE OR REPLACE VIEW vw_product_sales AS

SELECT

    sku_name,

    category,

    ROUND(SUM(net_sales)::numeric,2) AS revenue,

    SUM(units_sold) AS units

FROM fmcg_sales

GROUP BY

    sku_name,

    category

ORDER BY revenue DESC;


## 
CREATE OR REPLACE VIEW vw_promotion_summary AS

SELECT

    promo_flag,

    COUNT(*) AS transactions,

    ROUND(AVG(net_sales)::numeric,2) AS average_sales,

    ROUND(SUM(net_sales)::numeric,2) AS total_sales

FROM fmcg_sales

GROUP BY promo_flag;