# Requirements — Q3 2026 Acquisition Campaign Analysis

> **Mizan Yatırım is a fictional company.** It is modelled on a participation-finance (Islamic-compliant) brokerage. All data in this project is synthetic.

## 1. Business request

The Marketing Manager ran three new-investor acquisition campaigns in Q3 2026 and is planning the Q4 budget:

| Campaign | Channel | Q3 cost (TRY) |
|---|---|---|
| "İlk Hissem" | Social media ads | 1,200,000 |
| Bank app cross-sell | Banner + push in the group bank's mobile app (existing bank customers) | 300,000 |
| Creator partnerships | Finance content creators | 900,000 |
| **Total** | | **2,400,000** |

Questions asked:

1. Which campaign performed best?
2. How should the Q4 budget (same total, 2.4M TRY) be split across channels?
3. A stock promoted in the campaigns lost its participation-finance compliance in the **August screening**. What was the impact on the customers holding it?

## 2. Clarifications agreed with the Marketing Manager

- **Primary KPI** is the number of **active investors**. Customers who open an account and never trade, or trade once and stop, are not considered valuable. Revenue also matters; the analyst proposes how to combine the two.
- **Budget:** no channel will be shut down completely, but the split can change. A concrete percentage split is expected.
- **Compliance impact** is measured from the customer side: how many customers held the stock, what they did after the notification sent in August (sold and switched, sold and stayed in cash, kept holding), and whether customers were lost. A recommendation for the period before the February screening is expected.
- **Attribution:** each customer opens an account with a single campaign code (campaign link or promo code). Customers without a code are **organic**.

## 3. Participation-finance compliance rules

- Instruments are screened **twice a year, at the start of February and August**. Compliance status can only change on a screening date and stays fixed between screenings.
- **Business-activity screen:** companies whose core business is interest-based finance, alcohol, gambling or similar prohibited activities are excluded.
- **Financial-ratio screen:** companies whose interest-bearing debt or interest income exceed set thresholds are non-compliant. *(Thresholds in this project are illustrative; in practice they are set by index rules and the advisory board.)*
- A trade is evaluated against the compliance status of the **screening period in which the trade date falls**.

## 4. Metrics

### 4.1 Campaign comparison

All per-customer metrics use a **fixed 30-day window starting on the account-opening date**, so customers acquired in July and September are compared on equal terms.

| Metric | Definition |
|---|---|
| New customers | Distinct customers who opened an account in Q3 with the campaign's code |
| Activation rate | Share of new customers with at least one trade in their first 30 days |
| **Active investor (primary KPI)** | Customer who traded on **at least 2 different days** in their first 30 days |
| Cost per active investor (CAC) | Campaign cost / number of active investors |
| 30-day commission revenue | Total commission in each customer's first 30 days (total and per customer) |
| Payback period | CAC / monthly commission per active investor — months needed to recover acquisition cost |
| Trading volume | Supporting metric, read together with revenue |
| Retention | Share of customers who also traded between day 31 and day 60 |

### 4.2 Compliance impact

| Metric | Definition |
|---|---|
| Affected customers | Customers holding the stock on the August screening date |
| Post-notification behaviour | Within 30 days of the notification: sold and bought a compliant stock / sold and stayed in cash / kept holding |
| Customer loss | Activity rate of affected customers 60 days after screening, compared with unaffected customers |

## 5. Scope

- **Population:** customers who opened an account between **1 Jul 2026 and 30 Sep 2026**, through one of the three campaigns or organically.
- **Organic customers** are included as a **baseline** to estimate each campaign's incremental contribution.
- **Data cut-off:** 7 Oct 2026.
- **Maturity rule:** 30-day metrics only include customers who opened their account on or before **7 Sep 2026**. Later customers are reported separately as *immature*. 60-day metrics follow the same logic.

## 6. Data requirements

| Table | Content |
|---|---|
| `customers` | Customer, account-opening date, campaign code, existing bank customer flag, age band, city |
| `campaigns` | Campaign, channel, start/end date, cost |
| `funnel_events` | App install → account opened → first deposit → first trade |
| `trades` | Trade: customer, instrument, date, buy/sell, amount, commission |
| `instruments` | Instrument, type (stock, fund, lease certificate / sukuk), sector |
| `instrument_compliance` | Compliance history per screening period: compliant flag, reason, valid_from, valid_to |
| `notifications` | Customer, notification type, sent date, opened flag |

## 7. Deliverables

1. SQL data-quality checks and analysis queries (BigQuery)
2. Findings with **action recommendations**, including a proposed Q4 budget split
3. A short PDF presentation for the Marketing Manager
4. This repository, documented

## 8. Out of scope

- Multi-touch attribution (one campaign per customer is assumed)
- Long-term customer lifetime value beyond the payback estimate
- Statistical causal inference; organic customers are used as a descriptive baseline only
