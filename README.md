# 💰 RupeeIQ

> **Personal Finance Intelligence System for Indian Students**  
> Know Your Money. Know Yourself.

![Python](https://img.shields.io/badge/Python-3.11.9-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.57-FF4B4B?style=flat-square&logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.8-orange?style=flat-square&logo=scikit-learn)
![Plotly](https://img.shields.io/badge/Plotly-6.7-3F4F75?style=flat-square&logo=plotly)

---

## What is RupeeIQ?

RupeeIQ is a Streamlit web app that takes your bank transaction CSV and runs it through three AI-powered modules to deliver a complete financial intelligence report — your spending personality, a budget crisis forecast, and a personal money narrative.

Built for Indian college students. Understands Swiggy, Zomato, Ola, rent, salary credits, and the chaotic reality of student finances.

---

## Modules

### 🧠 Module 01 — Financial Personality Profiler
Matches your spending profile against 5 archetypes using Euclidean distance:

| Archetype | Description |
|---|---|
| 💎 Disciplined Saver | Consistently low spend across all categories |
| 🔥 Impulsive Spender | High variance, frequent impulse purchases |
| 🍜 The Foodie | Disproportionate food & delivery spend |
| 🎉 Social Butterfly | Entertainment and outing-heavy profile |
| ⚖️ Balanced Spender | Even distribution across all categories |

Output: archetype name, radar chart, bar chart, and a personalised tip.

### 🚨 Module 02 — Budget Crisis Predictor
Runs linear regression on your daily spending trend to forecast when your balance hits zero. Returns:
- Days remaining before crisis
- Average daily burn rate
- Crisis date
- Recovery plan (rule-based)

### 📖 Module 03 — Money Story Narrator
Detects 7 behavioural patterns from your transactions and generates a personalised narrative:
- Late night spending habits
- Weekend spending spikes
- Food-heavy allocation
- Impulse shopping signals
- No savings behaviour
- Health spend neglect
- Education investment

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit 1.57 + `components.html()` |
| Data | Pandas 3.0.2, NumPy 1.26.4 |
| ML | Scikit-learn 1.8 (LinearRegression, Euclidean distance) |
| Charts | Plotly 6.7 (dark terminal theme) |
| NLP | Rule-based pattern engine (no LLM dependency) |
| Fonts | IBM Plex Mono · Bebas Neue · DM Sans |

---

## Installation

```bash
git clone https://github.com/vishvrajsolanki-dev/rupeeiq.git
cd rupeeiq
pip install -r requirements.txt
```

Generate the sample dataset:
```bash
python data/synthetic_generator.py
```

Run the app:
```bash
streamlit run app.py
```

---

## CSV Format

Your transaction CSV must have these columns:

| Column | Type | Example |
|---|---|---|
| `date` | string / datetime | `2024-01-15` |
| `description` | string | `Swiggy Order` |
| `amount` | float | `245.0` |
| `category` | string | `Food` |
| `balance` | float | `8450.0` |
| `type` | string | `debit` / `credit` |

A sample CSV (`data/sample_transactions.csv`) is available for download inside the app sidebar.

---

## Project Structure

```
rupeeiq/
├── app.py                      # Main Streamlit UI
├── requirements.txt
├── data/
│   └── synthetic_generator.py  # Realistic Indian transaction generator
├── modules/
│   ├── personality_profiler.py # M1 — Euclidean archetype matching
│   ├── crisis_predictor.py     # M2 — Linear regression forecast
│   └── story_narrator.py       # M3 — Rule-based narrative engine
└── utils/
    ├── data_loader.py          # CSV loader + validator
    └── preprocessor.py         # Feature engineering + aggregations
```

---

## Deployment

Live on Streamlit Cloud: **https://rupeeiq-sjphk5ivzblxabz4uxbdvv.streamlit.app**

---

## Author

**Vishvrajsinh Solanki**  
[@vishvrajsolanki-dev](https://github.com/vishvrajsolanki-dev)