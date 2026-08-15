# 🧠 MindCare AI

An AI-based mental health monitoring companion built with **Streamlit** and the
**Google Gemini API**. Built as a student/portfolio project.

## Features

- **💬 AI Chat Companion** — supportive conversation powered by Gemini, with
  real-time sentiment analysis and automatic crisis-keyword detection that
  surfaces helpline resources.
- **📓 Journal** — write and revisit entries, each auto-tagged with sentiment.
- **📊 Mood Tracker** — quick daily 1–10 check-ins with trend charts.
- **🔥 Calorie Calculator** — BMR/TDEE via the Mifflin-St Jeor equation, with
  maintenance, deficit (weight loss), and surplus (weight gain) targets.
- **🧭 Dashboard** — mood + sentiment trends in one place.
- Simple username/password login with per-user history, stored in a local
  SQLite database (`mindcare.db`, created automatically on first run).

## Setup

1. **Clone/download this folder**, then install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > Uses Google's current `google-genai` SDK (the older
   > `google-generativeai` package is deprecated).

2. **Get a free Gemini API key**: https://aistudio.google.com/apikey

3. **Run the app**:

   ```bash
   streamlit run app.py
   ```

4. In the sidebar, paste your Gemini API key. Sign up for an account, log in,
   and use the pages in the sidebar to navigate.

## Project Structure

```
mindcare_ai/
├── app.py                          # Entry point: login/signup + API key setup
├── database.py                     # SQLite schema + all DB operations
├── ai_utils.py                     # Gemini chatbot, sentiment analysis, crisis detection
├── calorie_utils.py                # BMR/TDEE calorie calculations
├── requirements.txt
├── pages/
│   ├── 1_💬_Chat.py
│   ├── 2_📓_Journal.py
│   ├── 3_📊_Mood_Tracker.py
│   ├── 4_🔥_Calorie_Calculator.py
│   └── 5_🧭_Dashboard.py
└── mindcare.db                     # auto-created SQLite DB (git-ignore this)
```

## Notes for your report/viva

- **Why SQLite?** No server setup needed, perfect for a local/demo deployment,
  while still giving each user persistent history across sessions.
- **Why VADER for sentiment (not Gemini)?** It's a lightweight, rule-based
  sentiment tool that runs locally and instantly, so every chat/journal entry
  gets scored without burning extra API calls or adding latency. You can
  swap this for a Gemini-based sentiment classifier if you want an "everything
  through one model" story instead.
- **Crisis detection** uses simple keyword matching — good enough to
  demonstrate the concept, but a real deployment would want a proper trained
  classifier and, importantly, a human escalation path.
- **Security note:** password hashing here uses a single static salt for
  simplicity — for anything beyond a demo/project, use `bcrypt` or `argon2`
  with a per-user random salt.

## Important Disclaimer

This project is for educational purposes. It is **not** a substitute for
professional mental health care and does not diagnose any condition. If you
or someone you know is in crisis, please contact local emergency services or
a mental health helpline immediately.
