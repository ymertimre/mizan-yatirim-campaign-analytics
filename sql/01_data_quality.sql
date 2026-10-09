-- DQ-01: amount must equal quantity x price
SELECT trade_id, quantity, price_try, amount_try
FROM `mizan-campaign-analytics.raw.trades`
WHERE ABS(quantity * price_try - amount_try) > 0.01;

-- DQ-02 summary: how many trade_ids are duplicated, how many extra rows
SELECT
  COUNT(*)      AS duplicated_ids,
  SUM(cnt - 1)  AS extra_rows
FROM (
  SELECT trade_id, COUNT(*) AS cnt
  FROM `mizan-campaign-analytics.raw.trades`
  GROUP BY trade_id
  HAVING COUNT(*) > 1
);

-- DQ-02 detail: are duplicates identical rows or conflicting versions?
SELECT
  trade_id,
  COUNT(*)                            AS cnt,
  COUNT(DISTINCT TO_JSON_STRING(t))   AS distinct_versions
FROM `mizan-campaign-analytics.raw.trades` t
GROUP BY trade_id
HAVING COUNT(*) > 1;

-- DQ-03: every trade must belong to an existing customer
SELECT t.trade_id, t.customer_id, t.trade_date, t.instrument_id, t.amount_try
FROM `mizan-campaign-analytics.raw.trades` t
LEFT JOIN `mizan-campaign-analytics.raw.customers` c
  ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- DQ-04: no customer may buy an instrument that is non-compliant on the trade date
SELECT t.trade_id, t.customer_id, t.trade_date, t.instrument_id,
       t.amount_try, ic.reason
FROM `mizan-campaign-analytics.raw.trades` t
JOIN `mizan-campaign-analytics.raw.instrument_compliance` ic
  ON  t.instrument_id = ic.instrument_id
  AND t.trade_date >= ic.valid_from
  AND t.trade_date <  ic.valid_to
WHERE t.side = 'buy'
  AND NOT ic.is_compliant;

-- DQ-05: periods must start and end on the screening calendar (1 Feb / 1 Aug)
SELECT *
FROM `mizan-campaign-analytics.raw.instrument_compliance`
WHERE NOT (EXTRACT(DAY FROM valid_from) = 1 AND EXTRACT(MONTH FROM valid_from) IN (2, 8))
   OR NOT (valid_to = DATE '9999-12-31'
           OR (EXTRACT(DAY FROM valid_to) = 1 AND EXTRACT(MONTH FROM valid_to) IN (2, 8)));

-- DQ-06: compliance periods must be continuous (no gaps, no overlaps, open-ended last period)
WITH p AS (
  SELECT instrument_id, valid_from, valid_to,
         LEAD(valid_from) OVER (PARTITION BY instrument_id ORDER BY valid_from) AS next_from
  FROM `mizan-campaign-analytics.raw.instrument_compliance`
)
SELECT instrument_id, valid_from, valid_to, next_from,
  CASE
    WHEN next_from IS NULL      THEN 'last period not open-ended'
    WHEN valid_to < next_from   THEN 'gap'
    WHEN valid_to > next_from   THEN 'overlap'
  END AS issue
FROM p
WHERE (next_from IS NULL AND valid_to <> DATE '9999-12-31')
   OR valid_to <> next_from;

-- DQ-07: funnel steps must be in order
WITH f AS (
  SELECT user_id,
    MIN(IF(event_type = 'app_install',    event_date, NULL)) AS install_date,
    MIN(IF(event_type = 'account_opened', event_date, NULL)) AS account_date,
    MIN(IF(event_type = 'first_deposit',  event_date, NULL)) AS deposit_date,
    MIN(IF(event_type = 'first_trade',    event_date, NULL)) AS trade_date
  FROM `mizan-campaign-analytics.raw.funnel_events`
  GROUP BY user_id
)
SELECT *
FROM f
WHERE account_date < install_date
   OR deposit_date < account_date
   OR trade_date   < deposit_date;