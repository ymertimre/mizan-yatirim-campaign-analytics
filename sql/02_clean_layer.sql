CREATE OR REPLACE VIEW `mizan-campaign-analytics.analytics.trades_clean` AS
WITH dedup AS (
  SELECT *
  FROM `mizan-campaign-analytics.raw.trades`
  QUALIFY ROW_NUMBER() OVER (PARTITION BY trade_id ORDER BY trade_id) = 1
),
valid AS (
  SELECT t.*
  FROM dedup t
  JOIN `mizan-campaign-analytics.raw.customers` c
    ON t.customer_id = c.customer_id
)
SELECT
  v.*,
  ic.is_compliant AS is_compliant_at_trade,
  COALESCE(v.side = 'buy' AND NOT ic.is_compliant, FALSE) AS is_noncompliant_buy
FROM valid v
LEFT JOIN `mizan-campaign-analytics.raw.instrument_compliance` ic
  ON  v.instrument_id = ic.instrument_id
  AND v.trade_date >= ic.valid_from
  AND v.trade_date <  ic.valid_to;