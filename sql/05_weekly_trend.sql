-- Weekly app installs by source (wide format, one column per source)
SELECT
  DATE_TRUNC(event_date, WEEK(MONDAY))          AS week_start,
  COUNTIF(campaign_id = 'CMP_SOC')              AS social_media,
  COUNTIF(campaign_id = 'CMP_CRE')              AS content_creator,
  COUNTIF(campaign_id = 'CMP_BANK')             AS bank_app,
  COUNTIF(campaign_id IS NULL)                  AS organic
FROM `mizan-campaign-analytics.raw.funnel_events`
WHERE event_type = 'app_install'
GROUP BY week_start
ORDER BY week_start;