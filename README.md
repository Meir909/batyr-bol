# BATYR BOL - Educational Platform

BATYR BOL is an educational platform for learning Kazakh history and language through gamified missions. The platform is designed to attract investors and scale across Central Asia.

## Features

- Learn Kazakh history through interactive missions
- Practice Kazakh language with grammar exercises
- Voice mission challenges
- Progress tracking and leaderboards
- Bilingual support (Kazakh/Russian)
- Investor-ready platform with dedicated investment pages

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Update the `.env` file with your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   ```

4. For investor information, visit `/investors.html` after starting the server

## Running the Applications

### Website
```bash
python server.py
```
Access at: http://localhost:8000
Investor page: http://localhost:8000/investors.html

### Telegram Bot
```bash
python bb_bot.py
```
Enhanced investor bot available in `enhanced_investor_bot.py`

## Default Language

Kazakh is set as the default language for both the website and Telegram bot.

## Domain Configuration

For production deployment with custom domains, see `DEPLOYMENT_GUIDE.md`.

## Recommended Domains

1. batyrbol.kz
2. qazaqboly.kz
3. kazakhstanheroes.kz

## Feedback System

Users can submit feedback using the `/feedback` command in the Telegram bot. Feedback is saved to `feedback.json` and can be analyzed with `analyze_feedback.py`.

## Investor Relations

For investor inquiries, visit our dedicated investor page or contact us at invest@batyrbol.kz