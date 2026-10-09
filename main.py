import logging
from datetime import time, timezone

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    PollAnswerHandler,
)

from bot import config, database
from bot.handlers import daily, quiz, start, stats

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s", level=logging.INFO
)


async def post_init(app: Application) -> None:
    await database.init_db()
    await app.bot.set_my_commands(
        [
            BotCommand("quiz", "Get a new question"),
            BotCommand("level", "Change your level"),
            BotCommand("stats", "Your score and streak"),
            BotCommand("leaderboard", "Top learners"),
            BotCommand("daily", "Toggle the daily word"),
            BotCommand("help", "Show commands"),
        ]
    )


def main() -> None:
    app = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CommandHandler("help", start.help_command))
    app.add_handler(CommandHandler("level", start.level_command))
    app.add_handler(CommandHandler("quiz", quiz.quiz_command))
    app.add_handler(CommandHandler("stats", stats.stats))
    app.add_handler(CommandHandler("leaderboard", stats.leaderboard))
    app.add_handler(CommandHandler("daily", daily.daily_command))

    app.add_handler(CallbackQueryHandler(start.level_chosen, pattern=r"^level:"))
    app.add_handler(CallbackQueryHandler(quiz.next_quiz, pattern=r"^next_quiz$"))
    app.add_handler(PollAnswerHandler(quiz.handle_poll_answer))

    app.job_queue.run_daily(
        daily.send_daily_word,
        time=time(hour=config.DAILY_HOUR_UTC, minute=0, tzinfo=timezone.utc),
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
