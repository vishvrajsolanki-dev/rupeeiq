# RupeeIQ — Personal Finance Intelligence for Indian Students

**Upload a transaction CSV, get back a financial personality profile, a budget-crisis forecast, and a plain-language money story — three self-contained ML/NLP modules, zero external AI APIs.**

🔗 **Live:** [rupeeiq-sjphk5ivzblxabz4uxbdvv.streamlit.app](https://rupeeiq-sjphk5ivzblxabz4uxbdvv.streamlit.app)
📦 **Source:** [github.com/vishvrajsolanki-dev/rupeeiq](https://github.com/vishvrajsolanki-dev/rupeeiq)

---

## What It Does

Most students never see their own spending as data — just raw bank statements. RupeeIQ takes a transaction CSV and turns it into three distinct, personalised insights:

1. **Financial Personality Profiler** — classifies you into one of 5 archetypes (Disciplined Saver, Impulsive Spender, The Foodie, Social Butterfly, Balanced Spender) with a radar chart, category breakdown, and a personalised tip
2. **Budget Crisis Predictor** — fits a burn-rate trend to your spending and projects your zero-balance date, with a rule-based recovery plan
3. **Money Story Narrator** — detects 7 behavioural spending patterns (late-night spending, weekend spikes, no-savings behaviour, etc.) and writes a plain-language narrative summary

Built solo, from a blank project directory to a live deployed product, in a few days.

## Why It's Not "Another OpenAI Wrapper"

Every module runs **entirely locally** — no external LLM or AI API calls anywhere in the intelligence layer. Personality classification, crisis prediction, and narrative generation are all custom-built:

- **Personality classifier:** Euclidean distance to manually defined archetype centroid vectors — deliberately *not* K-Means (see below)
- **Crisis predictor:** `scikit-learn` `LinearRegression` on the daily spending time series
- **Story narrator:** rule-based NLP pattern detection across 7 behavioural signals

## The K-Means Pivot — the Actual Engineering Story

The first version of the personality profiler used K-Means clustering. It broke immediately: `ValueError: n_samples=1 should be >= n_clusters=5`. K-Means is a clustering algorithm for finding groups across many samples — it's structurally the wrong tool for classifying a *single* uploaded CSV against fixed categories.

The fix: define 5 archetype centroids as fixed vectors of spending percentages across categories, then classify the user by Euclidean distance to the nearest one. This is deterministic, always valid for a single sample, and more interpretable than a black-box cluster assignment — recognizing *why* K-Means failed and replacing it with the right tool, rather than forcing more data at it, is the actual signal here.

## Architecture

Single-file Streamlit app (`app.py`) backed by a modular, independently-testable Python package — each of the three analytical modules is fully decoupled from the UI layer.

**UI rendering:** Streamlit 1.57's `st.markdown` had a version-specific bug where triple-quoted HTML rendered as raw text instead of parsed HTML. Fixed by routing all complex UI blocks through `components.html()` (iframe-rendered, immune to the markdown parser) — this became a project-wide rule.

**State management:** Four-page router (`HOME`, `PERSONALITY`, `CRISIS RADAR`, `MONEY STORY`) via `st.session_state`, with all three analysis modules cached via `@st.cache_data` keyed on file bytes — meaning navigating between pages triggers **zero recomputation**.

**Design system:** Bloomberg Terminal × Indian street poster aesthetic — `IBM Plex Mono` for data readouts, `Bebas Neue` for display numbers, `DM Sans` for body text, an acid-green/cyan/amber palette, and a CSS scanline texture overlay.

## The Hardest Bug: Cross-Page Data Loss

The most persistent bug in the build. Each page originally called `uploaded_file.read()` independently — but `.read()` exhausts the file's buffer on first call, so every subsequent page got empty bytes back. Three iterations to actually fix it:

1. Store the file *object* in session state — buffer still exhausted, same failure
2. An "anchor file" pattern (via AI-assisted coding) added an `else` branch that cleared the stored file whenever `uploaded_file` returned `None` — which it does on *every* navigation rerun, silently wiping the data again
3. **Final fix:** call `uploaded_file.getvalue()` immediately on upload, store the raw bytes (not the file object) in session state, and remove the `else` branch entirely — bytes in session state survive reruns; file objects don't

Understanding *why* each attempt failed required reasoning about Streamlit's actual rerun execution model, not just pattern-matching a fix.

## Other Real Bugs, Real Fixes

- **Savings detection always `False`** — salary credits were being classified under the "Savings" category, making the raw amount always positive. Fixed by switching to a ratio check (savings < 5% of total spend).
- **Unrealistic synthetic data** — the first data generator produced ₹3L+ in "Rent" over 3 months. Rebuilt with a `CATEGORY_BLUEPRINT` defining realistic per-category frequency and amount ranges.
- **Windows encoding crash** — the ₹ symbol broke on Windows CMD (`cp1252` decode error). Fixed with explicit UTF-8 encoding and Rs. fallback in f-strings.
- **Deployment dependency conflict** — Streamlit Cloud's Python 3.14 runtime broke on a pinned `numpy` version incompatible with `pandas`. Fixed by removing the pin and letting the resolver pick a compatible transitive version.

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

## Tech Stack

Python · Streamlit · scikit-learn (LinearRegression) · Pandas · NumPy · Plotly · NLTK · Euclidean distance classifier · Rule-based NLP · Streamlit Cloud

## Notes

- Tested against synthetic Indian-student transaction data; not yet validated against real bank export formats (HDFC/SBI/ICICI).
- Layout built and tested for desktop; mobile rendering on Streamlit Cloud is unconfirmed.

---

*Built by [Vishvrajsinh Solanki](https://github.com/vishvrajsolanki-dev) — end-to-end ML product ownership: synthetic data generation, model design, custom UI, deployment, and debugging, solo.*
