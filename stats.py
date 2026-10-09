from telegram import Update
from telegram.ext import ContextTypes

from bot import database as db


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = await db.get_user(update.effective_user.id)
    if not user or user["total_answered"] == 0:
        await update.message.reply_text("No stats yet. Send /quiz to answer your first question!")
        return

    accuracy = round(100 * user["total_correct"] / user["total_answered"])
    await update.message.reply_text(
        "📊 Your stats\n"
        f"Level: {user['level'].capitalize()}\n"
        f"Answered: {user['total_answered']}\n"
        f"Correct: {user['total_correct']} ({accuracy}%)\n"
        f"🔥 Current streak: {user['streak']} day(s)\n"
        f"🏆 Best streak: {user['best_streak']} day(s)"
    )


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rows = await db.get_leaderboard(10)
    if not rows:
        await update.message.reply_text("The leaderboard is empty. Be the first with /quiz!")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 Top learners"]
    for i, r in enumerate(rows):
        name = r["first_name"] or r["username"] or "Learner"
        prefix = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{prefix} {name} - {r['total_correct']} correct")
    await update.message.reply_text("\n".join(lines))
