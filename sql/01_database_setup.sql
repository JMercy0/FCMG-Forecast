-- =====================================================
-- FMCG GLOBAL DEMAND PLANNING & FORECASTING
-- Database Setup Verification
-- =====================================================

-- Check current database
SELECT current_database();

-- Display all tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
ORDER BY table_name;

-- Count records
SELECT COUNT(*) AS total_rows
FROM fmcg_sales;

-- Count columns
SELECT COUNT(*) AS total_columns
FROM information_schema.columns
WHERE table_name='fmcg_sales';

-- Display table structure
SELECT
    ordinal_position,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name='fmcg_sales'
ORDER BY ordinal_position;

-- Preview data
SELECT *
FROM fmcg_sales
LIMIT 10;