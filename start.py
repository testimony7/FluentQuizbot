from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot import database as db

LEVELS = ["beginner", "intermediate", "advanced"]


def level_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(lvl.capitalize(), callback_data=f"level:{lvl}")] for lvl in LEVELS]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await db.upsert_user(user.id, user.username, user.first_name)
    await update.message.reply_text(
        f"👋 Hi {user.first_name}! I'm FluentQuizbot, your smart English learning companion.\n\n"
        "Pick your level to get started:",
        reply_markup=level_keyboard(),
    )


async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Choose your level:", reply_markup=level_keyboard())


async def level_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    level = query.data.split(":", 1)[1]
    user = query.from_user
    await db.upsert_user(user.id, user.username, user.first_name)
    await db.set_level(user.id, level)
    await query.edit_message_text(f"✅ Level set to {level.capitalize()}.\n\nSend /quiz to start!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Commands:\n"
        "/quiz - get a question (optionally: /quiz grammar)\n"
        "/level - change your level\n"
        "/stats - your score and streak\n"
        "/leaderboard - top learners\n"
        "/daily - turn the daily word on or off\n"
        "/help - show this message"
    )
