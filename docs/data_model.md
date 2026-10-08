# Data Model

Seven tables: three dimensions, one history (SCD Type 2) dimension and three fact tables. All data is synthetic.

## Tables

| Table | One row = | Type | Key |
|---|---|---|---|
| `campaigns` | One acquisition campaign | Dimension | `campaign_id` |
| `customers` | One customer (an app user who opened an investment account) | Dimension | `customer_id` |
| `instruments` | One tradable instrument | Dimension | `instrument_id` |
| `instrument_compliance` | One instrument's compliance status in one screening period | Dimension, SCD Type 2 | `instrument_id`, `valid_from` |
| `trades` | One buy or sell executed by a customer in one instrument | Fact | `trade_id` |
| `funnel_events` | One funnel step completed by one app user | Factless fact | `user_id`, `event_type` |
| `notifications` | One notification sent to one customer | Factless fact | `notification_id` |

## Relationships

```
campaigns 1 ── * funnel_events      (campaign_id)
campaigns 1 ── * customers          (campaign_id)
funnel_events * ── 0..1 customers   (user_id)
customers 1 ── * trades             (customer_id)
customers 1 ── * notifications      (customer_id)
instruments 1 ── * trades           (instrument_id)
instruments 1 ── * instrument_compliance (instrument_id)
```

## Conventions

- **Organic users and customers** have `campaign_id = NULL`. Use `COALESCE(campaign_id, 'ORGANIC')` when grouping.
- **App users vs customers:** every app install creates a `user_id`. A `customer_id` exists only after the account is opened. `funnel_events` is keyed by `user_id` because the first steps happen before the customer exists.
- **Funnel steps** (`event_type`), in order: `app_install` → `account_opened` → `first_deposit` → `first_trade`. Each user has at most one row per step.
- **Screening periods** start on **1 February** and **1 August**. Compliance status can only change on these dates.
- **Validity intervals are half-open:** `valid_from` is inclusive, `valid_to` is exclusive. The current period has `valid_to = 9999-12-31`. A trade's compliance is found with:

  ```sql
  ON  t.instrument_id = c.instrument_id
  AND t.trade_date >= c.valid_from
  AND t.trade_date <  c.valid_to
  ```

- **Holdings** are not stored. A customer's position in an instrument on a date is the cumulative sum of bought quantity minus sold quantity up to that date.
- **Currency:** all amounts are in TRY. `commission_try` is the brokerage commission earned on the trade.
- **Data cut-off:** 2026-10-07. No event after this date exists.

## Columns

### `campaigns`
| Column | Type | Description |
|---|---|---|
| `campaign_id` | STRING | Campaign code |
| `campaign_name` | STRING | Display name |
| `channel` | STRING | `social_media`, `bank_app`, `content_creator` |
| `start_date` / `end_date` | DATE | Campaign run dates |
| `cost_try` | NUMERIC | Total campaign cost in Q3 |

### `customers`
| Column | Type | Description |
|---|---|---|
| `customer_id` | STRING | Customer key |
| `user_id` | STRING | App user who became this customer |
| `campaign_id` | STRING | Acquisition campaign; NULL = organic |
| `account_open_date` | DATE | Account-opening date |
| `is_bank_customer` | BOOL | Already a customer of the group bank |
| `age_band` | STRING | `18-24`, `25-34`, `35-44`, `45-54`, `55+` |
| `city` | STRING | City of residence |

### `instruments`
| Column | Type | Description |
|---|---|---|
| `instrument_id` | STRING | Instrument key |
| `ticker` | STRING | Fictional ticker |
| `instrument_name` | STRING | Fictional name |
| `instrument_type` | STRING | `stock`, `participation_fund`, `lease_certificate`, `gold_fund` |
| `sector` | STRING | Sector (stocks) or asset class |

### `instrument_compliance`
| Column | Type | Description |
|---|---|---|
| `instrument_id` | STRING | Instrument key |
| `valid_from` | DATE | Period start (inclusive) |
| `valid_to` | DATE | Period end (exclusive); `9999-12-31` for the current period |
| `is_compliant` | BOOL | Compliant with participation-finance rules in this period |
| `reason` | STRING | Reason for non-compliance; NULL when compliant |

### `trades`
| Column | Type | Description |
|---|---|---|
| `trade_id` | STRING | Trade key |
| `customer_id` | STRING | Customer |
| `instrument_id` | STRING | Instrument |
| `trade_date` | DATE | Execution date |
| `side` | STRING | `buy` or `sell` |
| `quantity` | INT64 | Units traded |
| `price_try` | NUMERIC | Execution price per unit |
| `amount_try` | NUMERIC | `quantity × price_try` |
| `commission_try` | NUMERIC | Commission earned |
| `channel` | STRING | `mobile` or `advisor` |

### `funnel_events`
| Column | Type | Description |
|---|---|---|
| `user_id` | STRING | App user |
| `campaign_id` | STRING | Campaign that brought the user; NULL = organic |
| `event_type` | STRING | Funnel step |
| `event_date` | DATE | Date the step was completed |

### `notifications`
| Column | Type | Description |
|---|---|---|
| `notification_id` | STRING | Notification key |
| `customer_id` | STRING | Recipient |
| `notification_type` | STRING | `welcome` or `compliance_change` |
| `instrument_id` | STRING | Related instrument (compliance notifications only) |
| `sent_date` | DATE | Send date |
| `opened` | BOOL | Opened by the customer |
