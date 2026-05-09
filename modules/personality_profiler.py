# personality_profiler.py
# Module 1 — Financial Personality Profiler
# Uses K-Means clustering to classify spending
# personality into 5 archetypes

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

# ── ARCHETYPES ──────────────────────────────────
# These are the 5 spending personalities RupeeIQ
# can assign. Each has a name, emoji, description,
# and a tip for that personality type.

ARCHETYPES = {
    0: {
        "name":  "Survival Stacker",
        "emoji": "🏠",
        "desc":  "Most of your money goes to essentials — rent, utilities, education. You're keeping the lights on and grinding.",
        "tip":   "You're disciplined by necessity. Try setting aside even ₹500/month in a separate savings account."
    },
    1: {
        "name":  "Experience Chaser",
        "emoji": "🎯",
        "desc":  "You spend heavily on entertainment, food, and shopping. You live in the moment and value experiences.",
        "tip":   "You enjoy life — that's great. But try the 50-30-20 rule: 50% needs, 30% wants, 20% savings."
    },
    2: {
        "name":  "Impulsive Spender",
        "emoji": "🛍️",
        "desc":  "Shopping and entertainment dominate your spending. Purchases are frequent and varied.",
        "tip":   "Before any purchase over ₹500, wait 24 hours. You'll be surprised how often you skip it."
    },
    3: {
        "name":  "Disciplined Saver",
        "emoji": "💰",
        "desc":  "You consistently save and keep spending low across all categories. Rare and impressive.",
        "tip":   "You're already winning. Consider moving savings into a high-yield FD or index fund."
    },
    4: {
        "name":  "Balanced Builder",
        "emoji": "⚖️",
        "desc":  "Spending is spread evenly across categories with moderate saving. You're building stability.",
        "tip":   "Good foundation. Now pick ONE financial goal for the next 6 months and optimize toward it."
    },
}

# All 9 spending categories in a fixed order
# This order must stay consistent everywhere
CATEGORY_ORDER = [
    "Food", "Transport", "Entertainment",
    "Shopping", "Utilities", "Education",
    "Health", "Rent", "Savings"
]


def build_feature_vector(spending_profile):
    """
    Converts spending profile dict into a
    normalized numpy array for K-Means.

    Example input:
    {"Food": 24593, "Rent": 307074, ...}

    Example output:
    array([0.08, 0.03, 0.13, 0.23, 0.09,
           0.59, 0.16, 1.00, 0.31])

    Why normalize? K-Means uses distance.
    Without normalization, Rent (₹307k) would
    completely overpower Food (₹24k).
    Normalization brings everything to 0–1 scale.
    """
    # Build vector in fixed category order
    # Missing categories default to 0
    vector = np.array([
        spending_profile.get(cat, 0)
        for cat in CATEGORY_ORDER
    ]).reshape(1, -1)  # shape: (1, 9)

    # Normalize to 0–1 range
    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(vector)

    return normalized, scaler


def get_personality(spending_profile):
    """
    Finds the closest archetype by comparing
    the user's spending vector against 5
    manually defined archetype centers.

    Why this approach:
    We only have 1 user at a time. K-Means
    needs multiple samples. Instead we define
    5 archetype "ideal profiles" and measure
    which one the user is closest to using
    Euclidean distance.
    """
    vector, scaler = build_feature_vector(spending_profile)
    user_vec = vector[0]  # shape: (9,)

    # ── 5 Archetype Centers ─────────────────────────
    # Each row = one archetype's ideal spending pattern
    # Order matches CATEGORY_ORDER:
    # Food, Transport, Entertainment, Shopping,
    # Utilities, Education, Health, Rent, Savings

    # These values represent normalized spending weights
    # High value = spends a lot in that category
    archetype_centers = np.array([
        # 0 - Survival Stacker
        # High rent+education, low entertainment
        [0.3, 0.2, 0.1, 0.1, 0.5, 0.8, 0.3, 0.9, 0.2],

        # 1 - Experience Chaser
        # High food+entertainment+shopping, low savings
        [0.8, 0.5, 0.9, 0.7, 0.3, 0.2, 0.3, 0.4, 0.1],

        # 2 - Impulsive Spender
        # Very high shopping, high entertainment
        [0.5, 0.3, 0.8, 0.9, 0.4, 0.2, 0.2, 0.3, 0.1],

        # 3 - Disciplined Saver
        # Low spending everywhere, high savings
        [0.2, 0.2, 0.1, 0.1, 0.2, 0.3, 0.2, 0.4, 0.9],

        # 4 - Balanced Builder
        # Moderate spending across all categories
        [0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.4, 0.5, 0.5],
    ])

    # ── Find Closest Archetype ──────────────────────
    # Euclidean distance = straight-line distance
    # between two points in 9-dimensional space.
    # Smaller distance = more similar spending pattern.
    distances = np.linalg.norm(
        archetype_centers - user_vec, axis=1
    )

    # Pick the archetype with smallest distance
    cluster = int(np.argmin(distances))

    # Get the archetype details
    archetype = ARCHETYPES[cluster]

    # Calculate percentage breakdown
    total = sum(spending_profile.values()) or 1
    percentages = {
        cat: round((spending_profile.get(cat, 0)
                    / total) * 100, 1)
        for cat in CATEGORY_ORDER
    }

    return {
        "cluster":      cluster,
        "name":         archetype["name"],
        "emoji":        archetype["emoji"],
        "desc":         archetype["desc"],
        "tip":          archetype["tip"],
        "percentages":  percentages,
        "raw_spending": spending_profile,
        "distances":    distances.tolist(),
    }


def build_radar_chart(result):
    """
    Creates a radar (spider) chart showing
    spending distribution across all categories.

    A radar chart is perfect here because it
    shows ALL categories simultaneously and
    makes the personality shape visual.
    """
    categories   = CATEGORY_ORDER
    values       = [result["percentages"].get(c, 0)
                    for c in categories]

    # Radar charts need the first value repeated
    # at the end to close the polygon shape
    values_closed      = values + [values[0]]
    categories_closed  = categories + [categories[0]]

    fig = go.Figure()

    # The filled polygon
    fig.add_trace(go.Scatterpolar(
        r           = values_closed,
        theta       = categories_closed,
        fill        = "toself",
        fillcolor   = "rgba(99, 110, 250, 0.3)",
        line        = dict(color="#636EFA", width=2),
        name        = result["name"],
    ))

    fig.update_layout(
        polar = dict(
            radialaxis = dict(
                visible = True,
                range   = [0, max(values) + 5]
            )
        ),
        title      = f"{result['emoji']} Your Spending Radar",
        showlegend = False,
        height     = 420,
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font = dict(color="#FFFFFF")
    )

    return fig


def build_bar_chart(result):
    """
    Horizontal bar chart showing ₹ amount
    spent per category — sorted by value.
    """
    cats    = list(result["raw_spending"].keys())
    amounts = list(result["raw_spending"].values())

    # Sort by amount descending
    sorted_pairs = sorted(
        zip(cats, amounts),
        key=lambda x: x[1]
    )
    cats_sorted, amounts_sorted = zip(*sorted_pairs)

    fig = go.Figure(go.Bar(
        x           = amounts_sorted,
        y           = cats_sorted,
        orientation = "h",
        marker_color= "#636EFA",
        text        = [f"₹{a:,.0f}" for a in amounts_sorted],
        textposition= "outside",
    ))

    fig.update_layout(
        title         = "💸 Spending by Category",
        xaxis_title   = "Amount (₹)",
        height        = 380,
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font          = dict(color="#FFFFFF"),
        xaxis         = dict(color="#FFFFFF"),
        yaxis         = dict(color="#FFFFFF"),
    )

    return fig