SELECT

date,

SUM(net_sales) AS revenue

FROM fmcg_sales

GROUP BY date

ORDER BY date;

SELECT

year,
month,

SUM(net_sales) AS revenue

FROM fmcg_sales

GROUP BY

year,
month

ORDER BY

year,
month;


SELECT

year,
month,

SUM(units_sold) AS units

FROM fmcg_sales

GROUP BY

year,
month

ORDER BY

year,
month;


SELECT

year,
month,

SUM(promo_flag) AS promotional_days

FROM fmcg_sales

GROUP BY

year,
month

ORDER BY

year,
month;