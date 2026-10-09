import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.services import quiz_service

logger = logging.getLogger(__name__)


async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await db.upsert_user(user.id, user.username, user.first_name)
    subscribed = await db.toggle_daily(user.id)
    if subscribed:
        await update.message.reply_text("🔔 Daily word is ON. You'll get a new word every day.")
    else:
        await update.message.reply_text("🔕 Daily word is OFF.")


async def send_daily_word(context: ContextTypes.DEFAULT_TYPE) -> None:
    word = quiz_service.word_of_the_day()
    text = (
        "📚 Word of the day\n\n"
        f"{word['word']}\n"
        f"Meaning: {word['definition']}\n"
        f"Example: {word['example']}"
    )
    for user_id in await db.get_daily_subscribers():
        try:
            await context.bot.send_message(user_id, text)
        except Exception:
            logger.exception("Could not send daily word to %s", user_id)
