# data_loader.py
# Responsible for reading and validating
# the uploaded CSV file safely

import pandas as pd

# These are the exact columns our app expects
# If any are missing, we catch it early
REQUIRED_COLUMNS = [
    "date", "day_of_week", "hour",
    "category", "merchant",
    "amount", "type", "balance"
]

def load_csv(filepath):
    """
    Reads a CSV file and returns a DataFrame.
    If anything is wrong, returns None + error message.

    Returns:
        df      → cleaned DataFrame (or None if failed)
        error   → error message string (or None if success)
    """
    try:
        # Try reading the file
        df = pd.read_csv(filepath)

        # Check if file is completely empty
        if df.empty:
            return None, "❌ File is empty. Please upload a valid CSV."

        # Check if all required columns are present
        missing = [col for col in REQUIRED_COLUMNS
                   if col not in df.columns]

        if missing:
            return None, f"❌ Missing columns: {missing}"

        return df, None  # success — return df, no error

    except FileNotFoundError:
        return None, "❌ File not found. Check the path."

    except Exception as e:
        return None, f"❌ Could not read file: {str(e)}"


def get_summary(df):
    """
    Returns a quick summary dictionary about the data.
    Used to show stats at the top of the Streamlit app.
    """
    return {
        "total_transactions": len(df),
        "total_spent":        round(df[df["type"] == "debit"]["amount"].sum(), 2),
        "total_saved":        round(df[df["type"] == "credit"]["amount"].sum(), 2),
        "categories":         df["category"].nunique(),
        "date_range":         f"{df['date'].min()} → {df['date'].max()}",
        "top_category":       df[df["type"] == "debit"]["category"].value_counts().idxmax(),
    }