-- ============================================================================
-- 04_cac_payback.sql
-- Active investors, cost per active investor (CAC) and payback by source
--
-- Population : customers who opened an account in Q3 2026
-- Maturity   : 30-day metrics use only customers who opened on or before
--              2026-09-07 (every one of them has a full 30-day window)
-- Active     : traded on at least 2 different days in the first 30 days
-- Revenue    : commission in the first 30 days, excluding the 6 non-compliant
--              buys under compliance review (see docs/data_quality_log.md, DQ-04)
-- Cost       : campaign cost is allocated to the mature group in proportion to
--              its share of the campaign's customers
--              (assumption: spend is proportional to customers acquired)
-- Grain      : one row per source (campaign or ORGANIC)
-- ============================================================================

WITH customer_activity AS (
  -- One row per customer: activity in the first 30 days after account opening
  SELECT
    c.customer_id,
    COALESCE(c.campaign_id, 'ORGANIC')                                AS source,
    c.account_open_date,
    c.account_open_date <= DATE '2026-09-07'                          AS is_mature,
    COUNT(DISTINCT t.trade_date)                                      AS trade_days_30d,
    COALESCE(SUM(IF(t.is_noncompliant_buy, 0, t.commission_try)), 0)  AS commission_30d
  FROM `mizan-campaign-analytics.raw.customers` c
  LEFT JOIN `mizan-campaign-analytics.analytics.trades_clean` t
    ON  t.customer_id = c.customer_id
    AND t.trade_date >= c.account_open_date
    AND t.trade_date <  DATE_ADD(c.account_open_date, INTERVAL 30 DAY)
  GROUP BY c.customer_id, source, c.account_open_date
),

by_source AS (
  -- Customer counts and active-investor revenue per source
  SELECT
    source,
    COUNT(*)                                                          AS customers_all,
    COUNTIF(is_mature)                                                AS customers_mature,
    COUNTIF(is_mature AND trade_days_30d >= 2)                        AS active_investors,
    SUM(IF(is_mature AND trade_days_30d >= 2, commission_30d, 0))     AS commission_30d_active
  FROM customer_activity
  GROUP BY source
),

unit_economics AS (
  -- Each derived figure is computed once and reused below
  SELECT
    s.*,
    k.cost_try,
    k.cost_try * SAFE_DIVIDE(s.customers_mature, s.customers_all)     AS allocated_cost,
    SAFE_DIVIDE(s.commission_30d_active, s.active_investors)          AS commission_30d_per_active
  FROM by_source s
  LEFT JOIN `mizan-campaign-analytics.raw.campaigns` k   -- LEFT: keep ORGANIC (no cost)
    ON k.campaign_id = s.source
)

SELECT
  source,
  customers_all,
  customers_mature,
  active_investors,
  ROUND(SAFE_DIVIDE(active_investors, customers_mature), 3)           AS active_rate,
  cost_try,
  ROUND(allocated_cost, 0)                                            AS allocated_cost,
  ROUND(SAFE_DIVIDE(allocated_cost, active_investors), 0)             AS cac,
  ROUND(commission_30d_per_active, 1)                                 AS commission_30d_per_active,
  ROUND(SAFE_DIVIDE(SAFE_DIVIDE(allocated_cost, active_investors),
                    commission_30d_per_active), 1)                    AS payback_months
FROM unit_economics
ORDER BY cac;
