WITH country_sales AS (

SELECT

country,

SUM(net_sales) AS revenue

FROM fmcg_sales

GROUP BY country

)

SELECT *

FROM country_sales

ORDER BY revenue DESC

LIMIT 10;


WITH category_sales AS (

SELECT

category,

SUM(net_sales) AS revenue,

SUM(units_sold) AS units

FROM fmcg_sales

GROUP BY category

)

SELECT *

FROM category_sales

ORDER BY revenue DESC;


WITH promo_analysis AS (

SELECT

promo_flag,

AVG(net_sales) AS avg_sales

FROM fmcg_sales

GROUP BY promo_flag

)

SELECT *

FROM promo_analysis;