# Basalam Product Finder Bot

A minimal FastAPI application coupled with a Telegram bot to search cosmetic products from Basalam shops. Users can send multiple product names in one message and receive stalls that stock all requested items.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the keys.
   ```bash
   cp .env.example .env
   ```
3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The Telegram bot starts automatically in polling mode on server start.

## Environment Variables
- `BOT_TOKEN`: Telegram bot token.
- `GEMINI_API_KEY`: API key for Gemini language model (optional in mock mode).

## Notes
Data is mocked for demonstration and should be replaced with real Basalam APIs or database queries in production.
