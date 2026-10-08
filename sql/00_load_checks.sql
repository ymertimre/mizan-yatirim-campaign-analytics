-- Her tablodaki satır sayısı
SELECT table_id, row_count
FROM `mizan-campaign-analytics.raw.__TABLES__`
ORDER BY table_id;

-- BigQuery'nin her kolona atadığı veri tipi
SELECT table_name, column_name, data_type
FROM `mizan-campaign-analytics.raw.INFORMATION_SCHEMA.COLUMNS`
ORDER BY table_name, ordinal_position;