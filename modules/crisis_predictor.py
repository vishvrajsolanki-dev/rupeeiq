# crisis_predictor.py
# Module 2 — Budget Crisis Predictor
# Uses Linear Regression to predict when
# the user's balance will hit zero

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta


def predict_crisis(daily_spending_df, current_balance):
    """
    Takes daily spending history + current balance.
    Returns prediction of when money runs out.

    Parameters:
        daily_spending_df : DataFrame with columns
                            [date, daily_total]
        current_balance   : float — money available now

    Returns dict with:
        - crisis_date     : predicted date of ₹0
        - days_remaining  : how many days until crisis
        - avg_daily_spend : average spend per day
        - burn_rate       : regression slope (spend/day)
        - recovery_plan   : list of saving suggestions
        - is_safe         : True if no crisis predicted
    """

    # ── 1. Prepare data for regression ─────────────
    # Convert dates to numbers (day 0, 1, 2, 3...)
    # because LinearRegression needs numbers, not dates

    df = daily_spending_df.copy()
    df = df.sort_values("date").reset_index(drop=True)

    # X = day number (0, 1, 2, 3, ...)
    # Y = how much was spent that day
    X = np.arange(len(df)).reshape(-1, 1)
    Y = df["daily_total"].values

    # ── 2. Train the regression model ──────────────
    # fit() = "learn the pattern from this data"
    # The model finds the best straight line through
    # all the daily spending points
    model = LinearRegression()
    model.fit(X, Y)

    # burn_rate = slope of the line
    # = average daily spending increase/decrease
    # Example: 850.5 means spending ₹850.5/day
    burn_rate       = float(model.coef_[0])
    avg_daily_spend = float(np.mean(Y))

    # Use average daily spend for crisis prediction
    # (more stable than using the slope alone)
    daily_rate = max(avg_daily_spend, 1)  # avoid div/0

    # ── 3. Predict crisis date ──────────────────────
    # How many days until balance hits ₹0?
    # days = current_balance / daily_spend_rate
    days_until_zero = int(current_balance / daily_rate)

    today      = datetime.today()
    crisis_date = today + timedelta(days=days_until_zero)

    # Is this actually a problem?
    # If days_remaining > 30, user is safe this month
    is_safe = days_until_zero >= 30

    # ── 4. Generate recovery plan ──────────────────
    recovery_plan = _build_recovery_plan(
        current_balance,
        avg_daily_spend,
        days_until_zero,
        daily_spending_df
    )

    return {
        "crisis_date":      crisis_date.strftime("%B %d, %Y"),
        "days_remaining":   days_until_zero,
        "avg_daily_spend":  round(avg_daily_spend, 2),
        "burn_rate":        round(burn_rate, 2),
        "is_safe":          is_safe,
        "recovery_plan":    recovery_plan,
        "daily_df":         df,
        "model":            model,
        "X":                X,
        "Y":                Y,
    }


def _build_recovery_plan(balance, daily_rate,
                          days_left, daily_df):
    """
    Generates specific ₹-amount saving suggestions
    based on actual spending patterns.

    Returns list of suggestion strings.
    """
    suggestions = []

    # How much would we need to save per day
    # to make the money last 30 days?
    target_daily = balance / 30
    gap          = daily_rate - target_daily

    if gap <= 0:
        suggestions.append(
            "✅ You're on track! Current spending "
            "is sustainable for 30+ days."
        )
        return suggestions

    # Calculate specific cuts needed
    suggestions.append(
        f"⚠️ Reduce daily spending by "
        f"₹{gap:.0f} to last the full month."
    )

    # Food cut suggestion (assume 20% of daily is food)
    food_cut = round(daily_rate * 0.20 * 0.40, 0)
    suggestions.append(
        f"🍔 Cut food delivery by 40% → save "
        f"~₹{food_cut:.0f}/day"
    )

    # Entertainment cut (assume 15% of daily)
    ent_cut = round(daily_rate * 0.15 * 0.50, 0)
    suggestions.append(
        f"🎬 Reduce entertainment by 50% → save "
        f"~₹{ent_cut:.0f}/day"
    )

    # Weekend spending suggestion
    weekend_df  = daily_df.copy()
    weekday_avg = round(
        daily_df["daily_total"].mean(), 2
    )
    suggestions.append(
        f"📅 Your avg daily spend is ₹{weekday_avg}. "
        f"Set a daily limit of ₹{target_daily:.0f}."
    )

    return suggestions


def build_crisis_chart(result):
    """
    Line chart showing:
    - Actual daily spending (blue line)
    - Regression trend line (orange dashed)
    - Crisis point marker (red dot)
    """
    df    = result["daily_df"]
    model = result["model"]
    X     = result["X"]
    Y     = result["Y"]

    # Predicted values from regression line
    Y_pred = model.predict(X)

    # Extend prediction 15 days into future
    future_X    = np.arange(
        len(df), len(df) + 15
    ).reshape(-1, 1)
    future_Y    = model.predict(future_X)
    future_dates = [
        df["date"].iloc[-1] + timedelta(days=i+1)
        for i in range(15)
    ]

    fig = go.Figure()

    # Actual spending line
    fig.add_trace(go.Scatter(
        x    = df["date"],
        y    = Y,
        mode = "lines+markers",
        name = "Actual Spending",
        line = dict(color="#636EFA", width=2),
        marker = dict(size=4),
    ))

    # Regression trend line
    fig.add_trace(go.Scatter(
        x    = df["date"],
        y    = Y_pred,
        mode = "lines",
        name = "Trend",
        line = dict(color="#FFA15A",
                    width=2, dash="dash"),
    ))

    # Future prediction
    fig.add_trace(go.Scatter(
        x    = future_dates,
        y    = future_Y,
        mode = "lines",
        name = "Forecast",
        line = dict(color="#EF553B",
                    width=2, dash="dot"),
    ))

    fig.update_layout(
        title         = "📉 Daily Spending Trend & Forecast",
        xaxis_title   = "Date",
        yaxis_title   = "Amount Spent (₹)",
        height        = 400,
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font          = dict(color="#FFFFFF"),
        xaxis         = dict(color="#FFFFFF",
                             gridcolor="#333"),
        yaxis         = dict(color="#FFFFFF",
                             gridcolor="#333"),
        legend        = dict(font=dict(color="#FFFFFF")),
    )

    return fig