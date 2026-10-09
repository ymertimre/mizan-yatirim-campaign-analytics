# Data Quality Log

Each check tests one business rule and returns the rows that break it. Zero rows = passed.
Queries: [`sql/01_data_quality.sql`](../sql/01_data_quality.sql). Raw tables are never modified; fixes are applied in the clean layer (`analytics` dataset).

Checks that return zero rows were validated with a negative test: synthetic rows that break the rule are added to the query input to confirm the check catches them, then removed.

| Check | Rule | Rows | Finding | Decision |
|---|---|---|---|---|
| DQ-01 | `amount_try = quantity × price_try` (tolerance 0.01) | 0 | Passed | — |
| DQ-02 | `trade_id` is unique | 15 | 15 `trade_id`s appear twice; all copies are identical rows (double load) | Keep one row per `trade_id` in the clean layer |
| DQ-03 | Every trade belongs to an existing customer | 4 | Customer IDs `C9999xx` not in `customers`; likely test or foreign-system records | Excluded from analysis; reported to source team |
| DQ-04 | No buys of an instrument that is non-compliant on the trade date | 6 | Buys of INS001 (NVTEK) after it lost compliance in the 1 Aug screening; trade IDs are consecutive but dates spread Aug–Sep | Escalated to compliance team; flagged in the clean layer and excluded from campaign revenue metrics |
| DQ-05 | Compliance periods start and end on the screening calendar (1 Feb / 1 Aug) | 2 | INS014 period 1 Feb–1 Aug split at 15 May; compliance status is the same on both sides | No impact on analysis; reported to data owner |
| DQ-06 | Compliance periods are continuous (no gaps, overlaps or closed last period) | 0 | Passed (negative-tested) | — |
| DQ-07 | Funnel steps are complete and in order (install → account → deposit → first trade) | 0 | Passed (negative-tested) | — |
