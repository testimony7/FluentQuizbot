import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.services import quiz_service

logger = logging.getLogger(__name__)


async def send_quiz(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int,
                    category: str | None = None) -> None:
    user = await db.get_user(user_id)
    level = user["level"] if user else "beginner"

    q = quiz_service.get_question(level, category)
    if q is None:
        await context.bot.send_message(chat_id, "No questions found for that choice yet. Try /quiz again.")
        return

    msg = await context.bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type=Poll.QUIZ,
        correct_option_id=q["answer"],
        explanation=q.get("explanation"),
        is_anonymous=False,  # required so we receive the user's answer
    )
    await db.save_poll(msg.poll.id, user_id, q["answer"], q["category"])


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await db.upsert_user(user.id, user.username, user.first_name)

    category = context.args[0].lower() if context.args else None
    if category and category not in quiz_service.categories():
        await update.message.reply_text(
            "Unknown category. Choose one of: " + ", ".join(quiz_service.categories())
        )
        return
    await send_quiz(context, update.effective_chat.id, user.id, category)


async def next_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await send_quiz(context, query.message.chat_id, query.from_user.id)


async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.poll_answer
    if answer.user is None or not answer.option_ids:
        return

    poll = await db.pop_poll(answer.poll_id)
    if poll is None:
        return

    correct = answer.option_ids[0] == poll["correct_option"]
    user = await db.record_answer(answer.user.id, correct)
    if user is None:
        return

    text = ("✅ Correct!" if correct else "❌ Not quite.") + f"  🔥 Daily streak: {user['streak']}"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Next question ➡️", callback_data="next_quiz")]]
    )
    try:
        await context.bot.send_message(answer.user.id, text, reply_markup=keyboard)
    except Exception:
        logger.exception("Could not send follow-up to user %s", answer.user.id)
