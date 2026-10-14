-- ============================================================================
-- 03_funnel.sql
-- Acquisition funnel by source: install -> account -> deposit -> first trade
--
-- Population : app users who installed on or before 2026-09-07
--              (maturity rule: every user has had at least 30 days to convert)
-- Grain      : one row per source (campaign or ORGANIC)
-- Counts     : distinct users, so a duplicated event row cannot inflate a step
-- ============================================================================

WITH user_installs AS (
  -- Install date per user, used for the maturity filter
  SELECT
    user_id,
    event_date AS install_date
  FROM `mizan-campaign-analytics.raw.funnel_events`
  WHERE event_type = 'app_install'
),

step_counts AS (
  -- Number of users reaching each funnel step, per source
  SELECT
    COALESCE(f.campaign_id, 'ORGANIC')                                          AS source,
    COUNT(DISTINCT CASE WHEN f.event_type = 'app_install'    THEN f.user_id END) AS installs,
    COUNT(DISTINCT CASE WHEN f.event_type = 'account_opened' THEN f.user_id END) AS accounts,
    COUNT(DISTINCT CASE WHEN f.event_type = 'first_deposit'  THEN f.user_id END) AS deposits,
    COUNT(DISTINCT CASE WHEN f.event_type = 'first_trade'    THEN f.user_id END) AS first_trades
  FROM `mizan-campaign-analytics.raw.funnel_events` f
  JOIN user_installs u
    ON f.user_id = u.user_id
  WHERE u.install_date <= DATE '2026-09-07'
  GROUP BY source
)

SELECT
  source,
  installs,
  accounts,
  deposits,
  first_trades,
  ROUND(SAFE_DIVIDE(accounts,     installs), 3) AS install_to_account,
  ROUND(SAFE_DIVIDE(deposits,     accounts), 3) AS account_to_deposit,
  ROUND(SAFE_DIVIDE(first_trades, deposits), 3) AS deposit_to_trade,
  ROUND(SAFE_DIVIDE(first_trades, installs), 3) AS install_to_trade
FROM step_counts
ORDER BY install_to_trade DESC;
