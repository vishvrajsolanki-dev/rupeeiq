<div align="center">

# 💸 RupeeIQ

### Personal Finance Intelligence for Indian Students

Upload a transaction CSV. Get a financial personality profile, a budget-crisis forecast, and a plain-language money story — three self-contained ML/NLP modules, zero external AI APIs.

[![Live App](https://img.shields.io/badge/Live-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://rupeeiq-sjphk5ivzblxabz4uxbdvv.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-LinearRegression-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)

</div>

---

## What It Does

Most students never see their own spending as data — just raw bank statements. RupeeIQ takes a transaction CSV and turns it into three distinct, personalized insights:

| Module | What it does |
|---|---|
| 🧭 **Financial Personality Profiler** | Classifies you into one of 5 archetypes (Disciplined Saver, Impulsive Spender, The Foodie, Social Butterfly, Balanced Spender) with a radar chart, category breakdown, and a personalized tip |
| 📉 **Budget Crisis Predictor** | Fits a burn-rate trend to your spending and projects your zero-balance date, with a rule-based recovery plan |
| 📖 **Money Story Narrator** | Detects 7 behavioural spending patterns (late-night spending, weekend spikes, no-savings behaviour, etc.) and writes a plain-language narrative summary |

Built solo, from a blank project directory to a live deployed product, in a few days.

---

## Why It's Not "Another OpenAI Wrapper"

Every module runs entirely locally — **zero external LLM or AI API calls** anywhere in the intelligence layer.

- **Personality classifier** — Euclidean distance to manually defined archetype centroid vectors (deliberately *not* K-Means — see below)
- **Crisis predictor** — scikit-learn `LinearRegression` on the daily spending time series
- **Story narrator** — rule-based NLP pattern detection across 7 behavioural signals

### The K-Means Pivot — the Actual Engineering Story

The first version of the personality profiler used K-Means clustering. It broke immediately:

```
ValueError: n_samples=1 should be >= n_clusters=5
```

K-Means is a clustering algorithm for finding groups across many samples — structurally the wrong tool for classifying a single uploaded CSV against fixed categories.

**The fix:** define 5 archetype centroids as fixed vectors of spending percentages across categories, then classify the user by Euclidean distance to the nearest one. Deterministic, always valid for a single sample, and more interpretable than a black-box cluster assignment. Recognizing *why* K-Means failed and swapping in the right tool — instead of forcing more data at it — is the real signal here.

---

## Architecture

Single-file Streamlit app (`app.py`) backed by a modular, independently-testable Python package. Each of the three analytical modules is fully decoupled from the UI layer.

- **UI rendering** — Streamlit 1.57's `st.markdown` had a version-specific bug where triple-quoted HTML rendered as raw text instead of parsed HTML. Fixed by routing all complex UI blocks through `components.html()` (iframe-rendered, immune to the markdown parser) — became a project-wide rule.
- **State management** — Four-page router (`HOME`, `PERSONALITY`, `CRISIS RADAR`, `MONEY STORY`) via `st.session_state`, with all three analysis modules cached via `@st.cache_data` keyed on file bytes — navigating between pages triggers zero recomputation.
- **Design system** — Bloomberg Terminal × Indian street poster aesthetic: IBM Plex Mono for data readouts, Bebas Neue for display numbers, DM Sans for body text, an acid-green/cyan/amber palette, and a CSS scanline texture overlay.

---

## The Hardest Bug: Cross-Page Data Loss

The most persistent bug in the build. Each page originally called `uploaded_file.read()` independently — but `.read()` exhausts the file's buffer on first call, so every subsequent page got empty bytes back.

**Three iterations to actually fix it:**

1. Store the file object in session state → buffer still exhausted, same failure
2. An "anchor file" pattern (AI-assisted) added an `else` branch that cleared the stored file whenever `uploaded_file` returned `None` — which happens on *every* navigation rerun, silently wiping the data again
3. **Final fix:** call `uploaded_file.getvalue()` immediately on upload, store the raw bytes (not the file object) in session state, and remove the `else` branch entirely — bytes in session state survive reruns; file objects don't

Understanding why each attempt failed required reasoning about Streamlit's actual rerun execution model, not just pattern-matching a fix.

---

## Other Real Bugs, Real Fixes

| Bug | Fix |
|---|---|
| Savings detection always `False` | Salary credits were classified under "Savings," making the raw amount always positive → switched to a ratio check (`savings < 5%` of total spend) |
| Unrealistic synthetic data | First generator produced ₹3L+ in "Rent" over 3 months → rebuilt with a `CATEGORY_BLUEPRINT` defining realistic per-category frequency/amount ranges |
| Windows encoding crash | `₹` symbol broke on Windows CMD (`cp1252` decode error) → explicit UTF-8 encoding + `Rs.` fallback in f-strings |
| Deployment dependency conflict | Streamlit Cloud's Python 3.14 runtime broke on a pinned numpy version incompatible with pandas → removed the pin, let the resolver pick a compatible transitive version |

---

## Results

| Metric | Result |
|---|---|
| ML/NLP modules | 3, fully integrated and deployed |
| Financial archetypes | 5, with tuned centroid vectors + radar visualization |
| Behavioural patterns detected | 7, rule-based |
| Synthetic dataset | ~155 realistic transactions across 3 months, 10 categories |
| Bugs resolved | 8 total, 3 requiring architectural changes |
| External AI API calls | 0 |
| Build time | A few days, solo, blank repo → live deployment |

---

## Tech Stack

`Python` · `Streamlit` · `scikit-learn (LinearRegression)` · `Pandas` · `NumPy` · `Plotly` · `NLTK` · `Euclidean Distance Classifier` · `Rule-based NLP` · `Streamlit Cloud`

---

## Notes

- Tested against synthetic Indian-student transaction data; not yet validated against real bank export formats (HDFC/SBI/ICICI).
- Layout built and tested for desktop; mobile rendering on Streamlit Cloud is unconfirmed.

---

<div align="center">

Built by **Vishvrajsinh Solanki** — end-to-end ML product ownership: synthetic data generation, model design, custom UI, deployment, and debugging, solo.

[Live Demo](https://rupeeiq-sjphk5ivzblxabz4uxbdvv.streamlit.app) · [Source](https://github.com/vishvrajsolanki-dev/rupeeiq)

</div>
