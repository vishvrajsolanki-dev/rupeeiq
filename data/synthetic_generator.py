# synthetic_generator.py
# Realistic Indian student transaction generator
# Generates data month-by-month with controlled frequency
# so amounts and patterns are genuinely believable

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ── CONFIGURATION ──────────────────────────
MONTHLY_INCOME = 15000  # ₹ received on 1st of each month
NUM_MONTHS     = 3      # how many months to simulate
SEED           = 42
# ───────────────────────────────────────────

random.seed(SEED)
np.random.seed(SEED)

MERCHANTS = {
    "Food":          ["Swiggy", "Zomato", "Canteen",
                      "Tea Stall", "Dominos", "McDonald's",
                      "Mess", "Chai Point"],
    "Transport":     ["Ola", "Uber", "Bus Pass",
                      "Rapido", "Auto", "Petrol Pump"],
    "Entertainment": ["BookMyShow", "Netflix", "Spotify",
                      "Gaming", "Cafe", "Pub"],
    "Shopping":      ["Flipkart", "Amazon", "Myntra",
                      "D-Mart", "Reliance Trends", "Meesho"],
    "Utilities":     ["Electricity Board", "JIO Recharge",
                      "Airtel", "Wi-Fi", "Water Bill"],
    "Education":     ["Coursera", "Udemy", "Book Store",
                      "College Fee", "Stationery"],
    "Health":        ["Apollo Pharmacy", "Gym", "Doctor",
                      "MedPlus", "Yoga Class"],
    "Rent":          ["Room Rent", "PG Payment", "Hostel Fee"],
    "Savings":       ["GPay Savings", "FD Deposit",
                      "Piggy Bank", "SIP Investment"],
}

# ── CATEGORY BLUEPRINT ──────────────────────────────────────
# Each category defines:
#   freq_range : (min, max) transactions per month
#   amt_range  : (min, max) amount per transaction in ₹
#   txn_type   : debit or credit
# ───────────────────────────────────────────────────────────
CATEGORY_BLUEPRINT = {
    "Food":          {"freq": (15, 25), "amt": (80,   350), "type": "debit"},
    "Transport":     {"freq": (10, 20), "amt": (20,   200), "type": "debit"},
    "Entertainment": {"freq": (2,  5),  "amt": (100,  600), "type": "debit"},
    "Shopping":      {"freq": (2,  4),  "amt": (300, 2000), "type": "debit"},
    "Utilities":     {"freq": (2,  3),  "amt": (200,  700), "type": "debit"},
    "Education":     {"freq": (1,  3),  "amt": (200, 1500), "type": "debit"},
    "Health":        {"freq": (1,  2),  "amt": (100,  800), "type": "debit"},
    "Rent":          {"freq": (1,  1),  "amt": (4000,7000), "type": "debit"},
    "Savings":       {"freq": (1,  1),  "amt": (500, 2000), "type": "credit"},
}

def random_hour():
    """Returns a realistic hour weighted toward evening"""
    return np.random.choice(
        range(24),
        p=[0.01,0.01,0.01,0.01,0.01,0.01,
           0.03,0.04,0.05,0.05,0.05,0.05,
           0.06,0.06,0.05,0.05,0.06,0.07,
           0.08,0.08,0.07,0.04,0.03,0.02]
    )

def generate_transactions():
    """
    Generates realistic transactions month by month.

    For each month:
      1. Add salary credit on the 1st
      2. Add rent debit on the 1st
      3. For every other category, generate
         a realistic number of transactions
         spread across random days in that month
    """
    transactions = []
    balance      = MONTHLY_INCOME

    # Start from 1st of (NUM_MONTHS) months ago
    today      = datetime.today()
    start_year = today.year
    start_month= today.month - NUM_MONTHS

    # Handle month underflow (e.g. March - 3 = December prev year)
    if start_month <= 0:
        start_month += 12
        start_year  -= 1

    for month_offset in range(NUM_MONTHS):
        # Calculate current month/year
        m = start_month + month_offset
        y = start_year
        if m > 12:
            m -= 12
            y += 1

        # Days in this month
        if m == 12:
            days_in_month = (datetime(y + 1, 1, 1) - datetime(y, m, 1)).days
        else:
            days_in_month = (datetime(y, m + 1, 1) - datetime(y, m, 1)).days

        month_start = datetime(y, m, 1)

        # ── 1. SALARY CREDIT on the 1st ────────────
        balance += MONTHLY_INCOME
        transactions.append({
            "date":        month_start.strftime("%Y-%m-%d"),
            "day_of_week": month_start.strftime("%A"),
            "hour":        9,
            "category":    "Savings",
            "merchant":    "Salary Credit",
            "amount":      MONTHLY_INCOME,
            "type":        "credit",
            "balance":     round(balance, 2)
        })

        # ── 2. RENT on the 1st ──────────────────────
        rent_amt  = round(random.uniform(4000, 7000), 2)
        balance  -= rent_amt
        transactions.append({
            "date":        month_start.strftime("%Y-%m-%d"),
            "day_of_week": month_start.strftime("%A"),
            "hour":        10,
            "category":    "Rent",
            "merchant":    random.choice(MERCHANTS["Rent"]),
            "amount":      rent_amt,
            "type":        "debit",
            "balance":     round(balance, 2)
        })

        # ── 3. ALL OTHER CATEGORIES ─────────────────
        for category, blueprint in CATEGORY_BLUEPRINT.items():

            # Skip Rent and Savings — handled above
            if category in ("Rent", "Savings"):
                continue

            freq     = random.randint(*blueprint["freq"])
            amt_min  = blueprint["amt"][0]
            amt_max  = blueprint["amt"][1]
            txn_type = blueprint["type"]

            for _ in range(freq):
                # Random day in this month
                day  = random.randint(1, days_in_month)
                date = datetime(y, m, day)

                amount    = round(random.uniform(amt_min, amt_max), 2)
                merchant  = random.choice(MERCHANTS[category])
                hour      = random_hour()

                if txn_type == "debit":
                    balance -= amount
                else:
                    balance += amount

                transactions.append({
                    "date":        date.strftime("%Y-%m-%d"),
                    "day_of_week": date.strftime("%A"),
                    "hour":        int(hour),
                    "category":    category,
                    "merchant":    merchant,
                    "amount":      amount,
                    "type":        txn_type,
                    "balance":     round(balance, 2)
                })

        # ── 4. SAVINGS on last day of month ─────────
        sav_amt   = round(random.uniform(500, 2000), 2)
        last_day  = datetime(y, m, days_in_month)
        balance  += sav_amt
        transactions.append({
            "date":        last_day.strftime("%Y-%m-%d"),
            "day_of_week": last_day.strftime("%A"),
            "hour":        20,
            "category":    "Savings",
            "merchant":    random.choice(MERCHANTS["Savings"]),
            "amount":      sav_amt,
            "type":        "credit",
            "balance":     round(balance, 2)
        })

    # Sort chronologically
    df         = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])
    df         = df.sort_values("date").reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    return df


def save_csv(df, path="data/sample_transactions.csv"):
    df.to_csv(path, index=False)
    print(f"✅ Generated {len(df)} transactions")
    print(f"✅ Saved to: {path}")
    print(f"\n📊 Category breakdown:")
    print(df["category"].value_counts())
    print(f"\n💰 Amount stats:")
    print(df["amount"].describe().round(2))
    print(f"\n💳 Final balance: ₹{df['balance'].iloc[-1]:,.2f}")


if __name__ == "__main__":
    df = generate_transactions()
    save_csv(df)