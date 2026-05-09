# preprocessor.py
# Cleans raw CSV data and adds useful
# computed columns all 3 modules will need

import pandas as pd

def preprocess(df):
    """
    Takes raw DataFrame from data_loader.
    Returns cleaned, enriched DataFrame.

    Changes made:
    - Converts date column to proper datetime type
    - Extracts month, week number, day name
    - Adds time_of_day label (Morning/Afternoon etc.)
    - Ensures amount is always a positive number
    - Separates debits and credits cleanly
    """

    # ── 1. Fix date column ──────────────────────────
    # Convert string dates like "2024-03-15"
    # into proper Python datetime objects
    # This lets us do math with dates later
    df["date"] = pd.to_datetime(df["date"])

    # Extract useful time features from the date
    df["month"]       = df["date"].dt.month          # 1–12
    df["month_name"]  = df["date"].dt.strftime("%B") # "March"
    df["week_number"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_number"]  = df["date"].dt.day             # 1–31

    # ── 2. Add time of day label ────────────────────
    # Converts hour (0–23) into readable label
    # Used by the story narrator module
    def get_time_of_day(hour):
        if   5  <= hour < 12: return "Morning"
        elif 12 <= hour < 17: return "Afternoon"
        elif 17 <= hour < 21: return "Evening"
        elif 21 <= hour < 24: return "Night"
        else:                  return "Late Night"  # 0–4am

    df["time_of_day"] = df["hour"].apply(get_time_of_day)

    # ── 3. Ensure amount is always positive ─────────
    # Safety step — amounts should never be negative
    df["amount"] = df["amount"].abs()

    # ── 4. Separate debit and credit rows ───────────
    # debit  = money going OUT (spending)
    # credit = money coming IN (savings/income)
    df["is_debit"]  = df["type"] == "debit"
    df["is_credit"] = df["type"] == "credit"

    # ── 5. Add weekend flag ──────────────────────────
    # True if transaction happened on Sat or Sun
    df["is_weekend"] = df["day_of_week"].isin(
        ["Saturday", "Sunday"]
    )

    # ── 6. Sort by date ascending ───────────────────
    df = df.sort_values("date").reset_index(drop=True)

    return df


def get_spending_profile(df):
    """
    Builds a per-category spending summary.
    Used by Module 1 (Personality Profiler)
    and Module 3 (Story Narrator).

    Returns a dict like:
    {
      "Food": 4820.50,
      "Transport": 1200.00,
      ...
    }
    """
    debits = df[df["is_debit"]]  # only spending rows

    profile = (
        debits.groupby("category")["amount"]
        .sum()
        .round(2)
        .to_dict()
    )

    return profile


def get_daily_spending(df):
    """
    Returns total spending per day.
    Used by Module 2 (Crisis Predictor)
    for regression analysis.

    Returns a DataFrame with columns:
    date | daily_total
    """
    debits = df[df["is_debit"]]

    daily = (
        debits.groupby("date")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"amount": "daily_total"})
    )

    return daily