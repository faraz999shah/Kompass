# Kompass

**A money coach in your pocket, built for Deutsche Bank's Hackathon.** Bite-sized, game-like money lessons, personalized to your country, your confidence and your language.

<p align="center">
  <img src="docs/screenshots/01-welcome.png" width="250" alt="Welcome screen with language and country choices">
  <img src="docs/screenshots/06-roadmap.png" width="250" alt="Roadmap of five lessons on a winding path over a Mexican city scene">
  <img src="docs/screenshots/08-lesson-quiz.png" width="250" alt="Lesson quiz card with the correct answer highlighted green">
</p>

|  |  |
|---|---|
| 🌎 **Local** | US, Mexico or Kenya: local currency, banks and World Bank Findex facts |
| 🎯 **Personal** | Your weakest topics come first |
| 🧭 **Ask Kiko** | Ask a money question and it becomes a new lesson |
| 🔊 **Voice-first** | Every screen works by voice alone |
| 🗣️ **3 languages** | English, Spanish, Swahili |

---

## 1. Set up

Pick your language, country and life stage.

<p align="center">
  <img src="docs/screenshots/01-welcome.png" width="220" alt="Welcome screen in English with Mexico selected">
  <img src="docs/screenshots/17-welcome-es.png" width="220" alt="Welcome screen in Spanish">
  <img src="docs/screenshots/02-onboarding.png" width="220" alt="Onboarding questions about goals and comfort with money">
</p>

## 2. Find your starting point

Rate your confidence, take a 10-question quiz, and get your path.

<p align="center">
  <img src="docs/screenshots/03-confidence.png" width="220" alt="Confidence sliders for five money topics">
  <img src="docs/screenshots/04-quiz.png" width="220" alt="Baseline quiz question">
  <img src="docs/screenshots/05-path-preview.png" width="220" alt="Five personalized lessons, each with a reason">
</p>

## 3. Follow the roadmap

Finish a lesson to unlock the next. Kiko's lessons join the path with a **NEW** badge.

<p align="center">
  <img src="docs/screenshots/06-roadmap.png" width="250" alt="Roadmap with the current lesson and locked lessons">
  <img src="docs/screenshots/13-roadmap-bonus.png" width="250" alt="Roadmap with a NEW bonus lesson and the unit chest">
</p>

## 4. Learn one card at a time

Reveal, flip, quiz, spot the scam. Right answers glow, wrong ones cost a heart.

<p align="center">
  <img src="docs/screenshots/07-lesson-card.png" width="190" alt="Concept card about interest">
  <img src="docs/screenshots/08-lesson-quiz.png" width="190" alt="Multiple-choice card answered correctly">
  <img src="docs/screenshots/09-lesson-money-math.png" width="190" alt="Money maths question in Mexican pesos">
  <img src="docs/screenshots/10-success.png" width="190" alt="Success screen with plus 10 coins">
</p>

## 5. Ask Kiko, then spend your coins

<p align="center">
  <img src="docs/screenshots/12-ask-kiko.png" width="190" alt="Ask Kiko with a question added to the roadmap">
  <img src="docs/screenshots/14-shop.png" width="190" alt="Shop with streak freeze, extra heart and Kiko outfits">
  <img src="docs/screenshots/15-practice.png" width="190" alt="Practice tab for replaying lessons">
  <img src="docs/screenshots/16-leagues.png" width="190" alt="Leagues tab with streak and coins">
</p>

🔊 The speaker button on every screen reads it aloud, and the 🎤 lets you answer by voice.

---

## How it works

```
Expo app  ──▶  FastAPI  ──▶  scoring ranks your topics
                        ──▶  lesson templates + Findex facts  ──▶  LLM rewords them (checked, with a template fallback)
                        ──▶  speech-to-text for Ask Kiko  ──▶  new lesson on your path
```

**Stack:** Expo React Native · TypeScript · NativeWind · Zustand · TanStack Query · FastAPI · Pydantic · SQLite

## Run it

**API** (Python 3.11). Copy `.env.example` to `api/.env` and add your LLM key.

```bash
cd api && pip install -r requirements.txt && uvicorn app.main:app --reload
```

**App** (Expo SDK 54). Set `EXPO_PUBLIC_API_URL=http://127.0.0.1:8000` in `app/.env`. On a phone, use your computer's LAN address instead.

```bash
cd app && npm ci && npx expo start
```

Press **w** for the browser, or scan the QR code with Expo Go.

## Team

Built by [@faraz999shah](https://github.com/faraz999shah), [@willapat](https://github.com/willapat) and [@annabeltu](https://github.com/annabeltu).
