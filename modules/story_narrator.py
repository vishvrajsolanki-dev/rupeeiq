# modules/story_narrator.py
# Module 3 — Money Story Narrator
# Generates a personal financial narrative for the user
# based on their transactions, personality, and crisis result

import random

# ── PATTERN DETECTORS ──────────────────────────────────────

def _detect_late_night_spending(df):
    """Returns True if user frequently orders between 10pm–2am"""
    late = df[(df["hour"] >= 22) | (df["hour"] <= 2)]
    return len(late) >= 5

def _detect_weekend_spikes(df):
    """Returns True if weekend spending is 30%+ higher than weekday"""
    weekend = df[df["is_weekend"] == True]["amount"].sum()
    weekday = df[df["is_weekend"] == False]["amount"].sum()
    if weekday == 0:
        return False
    return (weekend / (weekday + weekend)) > 0.40

def _detect_food_heavy(spending_profile):
    """Returns True if Food is top-3 spending category"""
    sorted_cats = sorted(spending_profile.items(),
                         key=lambda x: x[1], reverse=True)
    top3 = [c[0] for c in sorted_cats[:3]]
    return "Food" in top3

def _detect_impulse_shopping(df):
    """Returns True if multiple Shopping txns happen on same day"""
    shopping = df[df["category"] == "Shopping"].copy()
    if shopping.empty:
        return False
    daily_counts = shopping.groupby("date").size()
    return (daily_counts >= 2).any()

def _detect_no_savings(spending_profile):
    """Returns True if intentional savings (non-salary) are zero"""
    # Salary credit inflates this — we check if savings
    # are less than 5% of total spend, indicating no real saving habit
    total = sum(spending_profile.values())
    savings = spending_profile.get("Savings", 0)
    if total == 0:
        return False
    return (savings / total) < 0.05

def _detect_health_neglect(spending_profile):
    """Returns True if Health spending is very low"""
    total = sum(spending_profile.values())
    health = spending_profile.get("Health", 0)
    if total == 0:
        return False
    return (health / total) < 0.02  # less than 2% on health

def _detect_education_investment(spending_profile):
    """Returns True if Education is a significant spend"""
    total = sum(spending_profile.values())
    edu = spending_profile.get("Education", 0)
    if total == 0:
        return False
    return (edu / total) > 0.15  # more than 15% on education

# ── OPENING LINE GENERATOR ──────────────────────────────────

def _get_opening(archetype_name):
    """Returns a personalized opening line based on personality"""
    openings = {
        "Survival Stacker": [
            "Every rupee you spend tells a story of resilience.",
            "You're playing the toughest financial game — and you're still in it.",
        ],
        "Experience Chaser": [
            "Your bank statement reads like a travel diary.",
            "You invest in moments, not things — and that's a valid choice.",
        ],
        "Impulsive Spender": [
            "Your money moves fast — sometimes faster than your thoughts.",
            "There's energy in how you spend. The trick is directing it.",
        ],
        "Disciplined Saver": [
            "Your transactions show something rare — intention.",
            "While others spend first and think later, you do the opposite.",
        ],
        "Balanced Builder": [
            "You've found something most people spend years chasing — balance.",
            "Your financial life has a quiet confidence to it.",
        ],
    }
    # Strip emoji from archetype name for dict lookup
    clean_name = archetype_name.split(" ", 1)[-1].strip() \
                 if archetype_name[0] in "🏠🎯🛍️💰⚖️" else archetype_name
    options = openings.get(clean_name, ["Your money tells an interesting story."])
    return random.choice(options)

# ── PATTERN LINES ───────────────────────────────────────────

def _get_pattern_lines(df, spending_profile):
    """Detects spending patterns and returns narrative sentences"""
    lines = []

    if _detect_late_night_spending(df):
        lines.append(
            "📱 You have a habit of spending late at night — those "
            "post-10pm orders add up more than you'd think."
        )

    if _detect_weekend_spikes(df):
        lines.append(
            "📅 Your weekends are significantly more expensive than your "
            "weekdays. The weekend version of you deserves a budget."
        )

    if _detect_food_heavy(spending_profile):
        lines.append(
            "🍔 Food is one of your top spending categories. That's not "
            "necessarily bad — but there's likely room to cook more."
        )

    if _detect_impulse_shopping(df):
        lines.append(
            "🛍️ There are days where you shopped multiple times. "
            "Impulse purchases are silent budget killers."
        )

    if _detect_no_savings(spending_profile):
        lines.append(
            "⚠️ There are no savings transactions in your data. "
            "Even ₹500/month in a recurring deposit changes your future."
        )

    if _detect_health_neglect(spending_profile):
        lines.append(
            "🏥 You spent very little on health. Don't wait for an "
            "emergency to start — preventive care is cheaper."
        )

    if _detect_education_investment(spending_profile):
        lines.append(
            "📚 A meaningful chunk of your money goes toward education. "
            "That's long-term thinking — keep it up."
        )

    if not lines:
        lines.append(
            "Your spending is fairly consistent with no major red flags detected."
        )

    return lines

# ── CRISIS CLOSING LINE ─────────────────────────────────────

def _get_crisis_line(crisis_result):
    """Adds a closing line based on crisis prediction"""
    if crisis_result.get("is_safe"):
        return (
            "✅ The good news? At your current pace, your balance "
            "should hold through the month. Stay consistent."
        )
    else:
        days = crisis_result.get("days_remaining", 0)
        if days <= 5:
            return (
                f"🚨 Your balance is critically low — estimated to run out "
                f"in {days} day(s). Immediate action needed."
            )
        else:
            return (
                f"⏳ At your current burn rate, your balance runs out in "
                f"{days} days. Small daily cuts will extend that significantly."
            )

# ── MAIN FUNCTION ───────────────────────────────────────────

def get_story(df, spending_profile, crisis_result, archetype_name):
    """
    Master function — generates the full money story narrative.

    Parameters:
        df             : preprocessed transactions DataFrame
        spending_profile: {category: total_amount} dict
        crisis_result  : output from predict_crisis()
        archetype_name : e.g. '💰 Disciplined Saver'

    Returns:
        dict with keys:
            opening   : str — personalized opening line
            patterns  : list of str — detected pattern lines
            closing   : str — crisis-based closing line
            full_story: str — everything joined as one paragraph
    """
    opening  = _get_opening(archetype_name)
    patterns = _get_pattern_lines(df, spending_profile)
    closing  = _get_crisis_line(crisis_result)

    full_story = opening + " " + " ".join(patterns) + " " + closing

    return {
        "opening":    opening,
        "patterns":   patterns,
        "closing":    closing,
        "full_story": full_story,
    }