"""
Synthetic data generator for the Mizan Yatırım campaign analytics case.

Mizan Yatırım is a fictional participation-finance brokerage. Every company,
ticker, customer and number produced here is synthetic.

Usage:
    python scripts/generate_mock_data.py            # writes CSVs to ./data
    python scripts/generate_mock_data.py --out data # custom folder

The generator is deterministic (fixed seed), so the same CSVs are produced
on every run.
"""

import argparse
import math
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 20261008
rng = np.random.default_rng(SEED)

Q3_START = date(2026, 7, 1)
Q3_END = date(2026, 9, 30)
CUTOFF = date(2026, 10, 7)
SCREENING_AUG = date(2026, 8, 1)
OPEN_END = date(9999, 12, 31)


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


Q3_DAYS = list(daterange(Q3_START, Q3_END))

# --------------------------------------------------------------------------
# Campaigns
# --------------------------------------------------------------------------
campaigns = pd.DataFrame(
    [
        ("CMP_SOC", "Ilk Hissem - Social Ads", "social_media", Q3_START, Q3_END, 1_200_000),
        ("CMP_BANK", "Bank App Cross-sell", "bank_app", Q3_START, Q3_END, 300_000),
        ("CMP_CRE", "Creator Partnerships", "content_creator", Q3_START, Q3_END, 900_000),
    ],
    columns=["campaign_id", "campaign_name", "channel", "start_date", "end_date", "cost_try"],
)

# Source profiles. ORG = organic (campaign_id NULL).
SOURCES = {
    "CMP_SOC": dict(users=18000, p_acc=0.18, p_dep=0.55, p_trd=0.60,
                    base=0.075, tau=18, amt_med=3500, bank_share=0.22,
                    ages=[0.30, 0.38, 0.18, 0.09, 0.05], promo_share=0.22, adv_share=0.02),
    "CMP_CRE": dict(users=7000, p_acc=0.31, p_dep=0.76, p_trd=0.90,
                    base=0.30, tau=9, amt_med=2600, bank_share=0.18,
                    ages=[0.46, 0.36, 0.11, 0.05, 0.02], promo_share=0.38, adv_share=0.01),
    "CMP_BANK": dict(users=3600, p_acc=0.64, p_dep=0.84, p_trd=0.78,
                     base=0.11, tau=150, amt_med=14000, bank_share=1.00,
                     ages=[0.05, 0.20, 0.30, 0.27, 0.18], promo_share=0.06, adv_share=0.15),
    "ORGANIC": dict(users=2600, p_acc=0.40, p_dep=0.70, p_trd=0.74,
                    base=0.10, tau=60, amt_med=7000, bank_share=0.30,
                    ages=[0.15, 0.35, 0.25, 0.15, 0.10], promo_share=0.08, adv_share=0.05),
}
AGE_BANDS = ["18-24", "25-34", "35-44", "45-54", "55+"]
CITIES = ["Istanbul", "Ankara", "Izmir", "Bursa", "Konya", "Kocaeli", "Kayseri", "Antalya", "Gaziantep", "Other"]
CITY_P = [0.42, 0.12, 0.08, 0.05, 0.05, 0.04, 0.03, 0.03, 0.03, 0.15]


def install_weights(source):
    """Daily install weights over Q3 for each source."""
    n = len(Q3_DAYS)
    idx = np.arange(n)
    if source == "CMP_SOC":
        w = 1.0 + 0.25 * (np.array([d.weekday() for d in Q3_DAYS]) >= 5)
    elif source == "CMP_BANK":
        # Limited audience: existing bank customers without an investment
        # account. Installs fall as the audience is used up.
        w = np.exp(-idx / 45.0)
    elif source == "CMP_CRE":
        # Creator videos land on specific days and create short bursts.
        w = np.full(n, 0.35)
        for day in [6, 20, 33, 47, 61, 75, 86]:
            for k in range(6):
                if day + k < n:
                    w[day + k] += 4.0 * math.exp(-k / 1.5)
    else:
        w = np.ones(n)
    return w / w.sum()


# --------------------------------------------------------------------------
# Instruments and compliance history
# --------------------------------------------------------------------------
instruments_spec = [
    # id, ticker, name, type, sector, base_price, compliance by period [2025-08, 2026-02, 2026-08], reason
    ("INS001", "NVTEK", "Nova Teknoloji", "stock", "Technology", 58.0, [1, 1, 0], "Interest-bearing debt ratio above threshold"),
    ("INS002", "MZYAZ", "Mizrak Yazilim", "stock", "Technology", 112.0, [1, 1, 1], None),
    ("INS003", "DGTLS", "Dijitalis Bilisim", "stock", "Technology", 74.0, [1, 1, 1], None),
    ("INS004", "ANDGD", "Anadolu Gida", "stock", "Food Retail", 240.0, [1, 1, 1], None),
    ("INS005", "BRKMR", "Bereketli Market", "stock", "Food Retail", 415.0, [1, 1, 1], None),
    ("INS006", "SFSAG", "Sifa Saglik", "stock", "Healthcare", 310.0, [1, 1, 1], None),
    ("INS007", "LKMED", "Lokum Medikal", "stock", "Healthcare", 21.5, [1, 1, 1], None),
    ("INS008", "CMNTO", "Cimento Toros", "stock", "Cement", 46.0, [1, 1, 1], None),
    ("INS009", "TRKCL", "Turkuaz Celik", "stock", "Steel", 33.0, [1, 1, 1], None),
    ("INS010", "EGENR", "Ege Enerji", "stock", "Energy", 18.4, [1, 1, 1], None),
    ("INS011", "YSLEN", "Yesil Enerji", "stock", "Energy", 27.9, [0, 1, 1], None),
    ("INS012", "SVNMK", "Savunma Makine", "stock", "Defence", 205.0, [1, 1, 1], None),
    ("INS013", "HVLJS", "Havaliman Lojistik", "stock", "Transport", 88.0, [1, 1, 1], None),
    ("INS014", "TKSTL", "Tekstil Anadolu", "stock", "Textile", 12.6, [1, 1, 1], None),
    ("INS015", "OTOYD", "Oto Yedek Parca", "stock", "Automotive", 64.0, [1, 1, 1], None),
    ("INS016", "GYOKN", "Konut GYO", "stock", "Real Estate", 9.8, [1, 1, 1], None),
    ("INS017", "TARIM", "Tarim Urunleri", "stock", "Agriculture", 37.5, [1, 1, 1], None),
    ("INS018", "KMYSN", "Kimya Sanayi", "stock", "Chemicals", 52.0, [1, 1, 0], "Interest income ratio above threshold"),
    # Never compliant: core business prohibited
    ("INS019", "KLBNK", "Klasik Bank", "stock", "Conventional Banking", 41.0, [0, 0, 0], "Core business: interest-based finance"),
    ("INS020", "ISTFK", "Istanbul Faktoring", "stock", "Conventional Finance", 15.2, [0, 0, 0], "Core business: interest-based finance"),
    ("INS021", "BRUIC", "Bira Icecek", "stock", "Beverages", 96.0, [0, 0, 0], "Core business: alcohol"),
    ("INS022", "SANSO", "Sans Oyunlari", "stock", "Gaming", 28.0, [0, 0, 0], "Core business: gambling"),
    # Participation products
    ("INS023", "KTF01", "Mizan Katilim Hisse Fonu", "participation_fund", "Equity Fund", 3.2, [1, 1, 1], None),
    ("INS024", "KTF02", "Mizan Teknoloji Katilim Fonu", "participation_fund", "Equity Fund", 2.4, [1, 1, 1], None),
    ("INS025", "KTF03", "Mizan Para Piyasasi Katilim Fonu", "participation_fund", "Money Market Fund", 1.9, [1, 1, 1], None),
    ("INS026", "SKK27", "Kira Sertifikasi 2027", "lease_certificate", "Lease Certificate", 100.0, [1, 1, 1], None),
    ("INS027", "SKK28", "Kira Sertifikasi 2028", "lease_certificate", "Lease Certificate", 100.0, [1, 1, 1], None),
    ("INS028", "ALTNF", "Mizan Altin Katilim Fonu", "gold_fund", "Gold", 4.6, [1, 1, 1], None),
]
instruments = pd.DataFrame(
    [(r[0], r[1], r[2], r[3], r[4]) for r in instruments_spec],
    columns=["instrument_id", "ticker", "instrument_name", "instrument_type", "sector"],
)
PERIODS = [(date(2025, 8, 1), date(2026, 2, 1)), (date(2026, 2, 1), date(2026, 8, 1)), (date(2026, 8, 1), OPEN_END)]

comp_rows = []
for r in instruments_spec:
    for (vf, vt), flag in zip(PERIODS, r[6]):
        reason = None if flag else (r[7] or "Financial ratio above threshold")
        comp_rows.append((r[0], vf, vt, bool(flag), reason))
instrument_compliance = pd.DataFrame(
    comp_rows, columns=["instrument_id", "valid_from", "valid_to", "is_compliant", "reason"]
)

# Prices: daily random walk per instrument
price = {}
for r in instruments_spec:
    p = r[5]
    vol = 0.004 if r[3] in ("lease_certificate", "participation_fund") else 0.018
    series = {}
    for d in daterange(Q3_START, CUTOFF):
        p = p * math.exp(rng.normal(0.0004, vol))
        series[d] = round(p, 2)
    price[r[0]] = series


def compliant_on(instr_id, d):
    for (vf, vt), flag in zip(PERIODS, next(x[6] for x in instruments_spec if x[0] == instr_id)):
        if vf <= d < vt:
            return bool(flag)
    return False


PROMO = "INS001"  # NVTEK, promoted in social and creator campaigns
TECH_ALTERNATIVES = ["INS002", "INS003", "INS024"]
GENERAL_POOL = [r[0] for r in instruments_spec if r[0] not in ("INS001",)]
GENERAL_W = np.array([3, 3, 3, 3, 3, 2, 2, 2, 3, 2, 3, 2, 2, 2, 1, 1, 2, 0, 0, 0, 0, 4, 2, 3, 2, 2, 3], dtype=float)

# --------------------------------------------------------------------------
# Users, funnel, customers
# --------------------------------------------------------------------------
funnel_rows, customer_rows = [], []
cust_meta = {}
user_seq, cust_seq = 0, 0

for src, prof in SOURCES.items():
    w = install_weights(src)
    install_idx = rng.choice(len(Q3_DAYS), size=prof["users"], p=w)
    for i in install_idx:
        user_seq += 1
        uid = f"U{user_seq:06d}"
        camp = None if src == "ORGANIC" else src
        d_inst = Q3_DAYS[i]
        funnel_rows.append((uid, camp, "app_install", d_inst))
        if rng.random() > prof["p_acc"]:
            continue
        d_acc = d_inst + timedelta(days=int(rng.choice([0, 0, 0, 1, 1, 2, 3, 5])))
        if d_acc > Q3_END:
            continue
        funnel_rows.append((uid, camp, "account_opened", d_acc))
        cust_seq += 1
        cid = f"C{cust_seq:06d}"
        is_bank = bool(rng.random() < prof["bank_share"])
        age = rng.choice(AGE_BANDS, p=prof["ages"])
        city = rng.choice(CITIES, p=CITY_P)
        customer_rows.append((cid, uid, camp, d_acc, is_bank, age, city))
        meta = dict(src=src, open=d_acc, first_trade=None)
        if rng.random() < prof["p_dep"]:
            d_dep = d_acc + timedelta(days=int(rng.choice([0, 0, 1, 1, 2, 3, 4, 6])))
            if d_dep <= CUTOFF:
                funnel_rows.append((uid, camp, "first_deposit", d_dep))
                if rng.random() < prof["p_trd"]:
                    d_ft = d_dep + timedelta(days=int(rng.choice([0, 0, 0, 1, 1, 2, 3, 5, 8])))
                    if d_ft <= CUTOFF:
                        funnel_rows.append((uid, camp, "first_trade", d_ft))
                        meta["first_trade"] = d_ft
        cust_meta[cid] = meta

funnel_events = pd.DataFrame(funnel_rows, columns=["user_id", "campaign_id", "event_type", "event_date"])
customers = pd.DataFrame(
    customer_rows,
    columns=["customer_id", "user_id", "campaign_id", "account_open_date", "is_bank_customer", "age_band", "city"],
)

# --------------------------------------------------------------------------
# Trades (day-by-day simulation with holdings)
# --------------------------------------------------------------------------
trade_rows, notif_rows = [], []
trade_seq, notif_seq = 0, 0


def add_trade(cid, iid, d, side, qty, channel):
    global trade_seq
    trade_seq += 1
    p = price[iid][d]
    amt = round(qty * p, 2)
    comm = round(max(amt * 0.002, 1.0), 2)
    trade_rows.append((f"T{trade_seq:07d}", cid, iid, d, side, int(qty), p, amt, comm, channel))


def pick_buy(src, prof, d):
    if d < SCREENING_AUG and rng.random() < prof["promo_share"]:
        return PROMO
    while True:
        iid = rng.choice(GENERAL_POOL, p=GENERAL_W / GENERAL_W.sum())
        if compliant_on(iid, d):
            return iid


# Customers affected by the August screening and their planned reaction
affected = {}

for cid, meta in cust_meta.items():
    notif_seq += 1
    notif_rows.append((f"N{notif_seq:06d}", cid, "welcome", None, meta["open"], bool(rng.random() < 0.55)))
    if meta["first_trade"] is None:
        continue
    src = meta["src"]
    prof = SOURCES[src]
    holdings = {}
    churned = False
    reaction = None
    held_at_screening = False
    for d in daterange(meta["first_trade"], CUTOFF):
        t = (d - meta["first_trade"]).days

        # The holder list is taken at the start of the screening day.
        if d == SCREENING_AUG:
            held_at_screening = holdings.get(PROMO, 0) > 0

        # Holders of the promoted stock are notified two days later.
        if d == SCREENING_AUG + timedelta(days=2) and held_at_screening:
            open_p = {"CMP_BANK": 0.82, "ORGANIC": 0.66, "CMP_SOC": 0.55, "CMP_CRE": 0.46}[src]
            opened = bool(rng.random() < open_p)
            notif_seq += 1
            notif_rows.append((f"N{notif_seq:06d}", cid, "compliance_change", PROMO, d, opened))
            probs = [0.55, 0.25, 0.20] if opened else [0.14, 0.26, 0.60]
            reaction = rng.choice(["switch", "cash", "keep"], p=probs)
            react_day = d + timedelta(days=int(rng.integers(1, 20)))
            affected[cid] = (reaction, react_day)

        if cid in affected and d == affected[cid][1]:
            reaction = affected[cid][0]
            if reaction in ("switch", "cash"):
                qty = holdings.pop(PROMO, 0)
                if qty > 0:
                    add_trade(cid, PROMO, d, "sell", qty, "mobile")
            if reaction == "switch":
                alt = rng.choice(TECH_ALTERNATIVES)
                qty = max(1, int(rng.lognormal(math.log(prof["amt_med"]), 0.6) / price[alt][d]))
                add_trade(cid, alt, d, "buy", qty, "mobile")
                holdings[alt] = holdings.get(alt, 0) + qty
            if reaction == "cash" and rng.random() < 0.6:
                churned = True
            continue

        if churned:
            continue

        if t == 0:
            p_day = 1.0
        else:
            p_day = prof["base"] * math.exp(-t / prof["tau"]) + 0.006
            if reaction == "cash":
                p_day *= 0.4
        if rng.random() > p_day:
            continue

        channel = "advisor" if rng.random() < prof["adv_share"] else "mobile"
        n_trades = int(rng.choice([1, 1, 1, 2, 2, 3]))
        for _ in range(n_trades):
            held = [k for k, v in holdings.items() if v > 0]
            if held and rng.random() < 0.38:
                iid = rng.choice(held)
                if iid == PROMO and d >= SCREENING_AUG and reaction == "keep":
                    continue
                qty = holdings[iid] if rng.random() < 0.5 else max(1, holdings[iid] // 2)
                add_trade(cid, iid, d, "sell", qty, channel)
                holdings[iid] -= qty
            else:
                iid = pick_buy(src, prof, d)
                amount = rng.lognormal(math.log(prof["amt_med"]), 0.8)
                qty = max(1, int(amount / price[iid][d]))
                add_trade(cid, iid, d, "buy", qty, channel)
                holdings[iid] = holdings.get(iid, 0) + qty

trades = pd.DataFrame(
    trade_rows,
    columns=["trade_id", "customer_id", "instrument_id", "trade_date", "side", "quantity",
             "price_try", "amount_try", "commission_try", "channel"],
)
notifications = pd.DataFrame(
    notif_rows, columns=["notification_id", "customer_id", "notification_type", "instrument_id", "sent_date", "opened"]
)

# --------------------------------------------------------------------------
# Real-world data issues (to be found in data-quality checks)
# --------------------------------------------------------------------------
# 1) Duplicate trade rows from a double load
dup = trades.sample(15, random_state=SEED)
trades = pd.concat([trades, dup], ignore_index=True)

# 2) Buys of the promoted stock after it became non-compliant
late_buyers = trades[(trades["trade_date"] >= SCREENING_AUG)].sample(6, random_state=SEED + 1)
extra = []
for _, r in late_buyers.iterrows():
    trade_seq += 1
    p = price[PROMO][r["trade_date"]]
    qty = int(rng.integers(20, 150))
    amt = round(qty * p, 2)
    extra.append((f"T{trade_seq:07d}", r["customer_id"], PROMO, r["trade_date"], "buy", qty, p, amt,
                  round(max(amt * 0.002, 1.0), 2), "mobile"))
trades = pd.concat([trades, pd.DataFrame(extra, columns=trades.columns)], ignore_index=True)

# 3) Trades whose customer does not exist
orphans = []
for k in range(4):
    trade_seq += 1
    d = Q3_DAYS[int(rng.integers(20, 90))]
    iid = "INS004"
    p = price[iid][d]
    orphans.append((f"T{trade_seq:07d}", f"C9999{k+1:02d}", iid, d, "buy", 10, p, round(10 * p, 2),
                    round(max(10 * p * 0.002, 1.0), 2), "mobile"))
trades = pd.concat([trades, pd.DataFrame(orphans, columns=trades.columns)], ignore_index=True)

# 4) A compliance row that starts outside the screening calendar
bad = instrument_compliance[(instrument_compliance["instrument_id"] == "INS014") &
                            (instrument_compliance["valid_from"] == date(2026, 2, 1))].index[0]
instrument_compliance.loc[bad, "valid_to"] = date(2026, 5, 15)
instrument_compliance = pd.concat([
    instrument_compliance,
    pd.DataFrame([("INS014", date(2026, 5, 15), date(2026, 8, 1), True, None)], columns=instrument_compliance.columns),
], ignore_index=True)

trades = trades.sort_values(["trade_date", "trade_id"], kind="stable").reset_index(drop=True)
instrument_compliance = instrument_compliance.sort_values(["instrument_id", "valid_from"]).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    tables = {
        "campaigns": campaigns,
        "customers": customers,
        "instruments": instruments,
        "instrument_compliance": instrument_compliance,
        "trades": trades,
        "funnel_events": funnel_events,
        "notifications": notifications,
    }
    for name, df in tables.items():
        path = os.path.join(args.out, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"{name:<22} {len(df):>8,} rows -> {path}")


if __name__ == "__main__":
    main()
