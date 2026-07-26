-- =====================================================
-- DATA VALIDATION
-- =====================================================

-- Total records
SELECT COUNT(*) AS total_rows
FROM fmcg_sales;

-- Distinct countries
SELECT COUNT(DISTINCT country) AS countries
FROM fmcg_sales;

-- Distinct cities
SELECT COUNT(DISTINCT city) AS cities
FROM fmcg_sales;

-- Distinct SKUs
SELECT COUNT(DISTINCT sku_id) AS skus
FROM fmcg_sales;

-- Distinct sales channels
SELECT COUNT(DISTINCT channel) AS channels
FROM fmcg_sales;

-- Date range
SELECT
MIN(date) AS first_date,
MAX(date) AS last_date
FROM fmcg_sales;