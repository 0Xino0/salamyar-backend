"""FastAPI entry point and Telegram bot startup."""

from fastapi import FastAPI
from dotenv import load_dotenv

from .telegram_bot import start_bot

load_dotenv()

app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    """Start the Telegram bot when the API starts."""
    start_bot()


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
