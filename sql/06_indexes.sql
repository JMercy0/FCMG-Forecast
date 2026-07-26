-- ============================================
-- Performance Indexes
-- ============================================

CREATE INDEX idx_date
ON fmcg_sales(date);

CREATE INDEX idx_country
ON fmcg_sales(country);

CREATE INDEX idx_city
ON fmcg_sales(city);

CREATE INDEX idx_channel
ON fmcg_sales(channel);

CREATE INDEX idx_sku
ON fmcg_sales(sku_id);

CREATE INDEX idx_category
ON fmcg_sales(category);

CREATE INDEX idx_brand
ON fmcg_sales(brand);

CREATE INDEX idx_supplier
ON fmcg_sales(supplier_id);

CREATE INDEX idx_promotion
ON fmcg_sales(promo_flag);

CREATE INDEX idx_country_date
ON fmcg_sales(country, date);