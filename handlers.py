import logging

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database import init_db

from scheduler import setup_scheduler
from admin import is_admin
from keyboards import admin_panel_keyboard


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    format=(
        "%(asctime)s - %(name)s - "
        "%(levelname)s - %(message)s"
    ),
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ==========================================
# PRIVATE CHAT CHECK
# ==========================================

def is_private_chat(update: Update) -> bool:
    chat = update.effective_chat

    return (
        chat is not None
        and chat.type == ChatType.PRIVATE
    )


# ==========================================
# ADMIN COMMAND
# ==========================================

async def admin_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    # Do not respond to /admin in groups or channels.
    if not is_private_chat(update):
        return

    user = update.effective_user
    message = update.effective_message

    if not user or not message:
        return

    if not is_admin(user.id):
        await message.reply_text(
            "⛔ You are not authorized to access the admin panel."
        )
        return

    await message.reply_text(
        "🛡️ <b>SF ARMY ADMIN PANEL</b>\n\n"
        "Select an option below:",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


# ==========================================
# ERROR HANDLER
# ==========================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "An exception occurred while processing an update:",
        exc_info=context.error,
    )


# ==========================================
# POST INITIALIZATION
# ==========================================

async def post_init(application: Application):
    setup_scheduler(application)

    logger.info(
        "Daily backup scheduler initialized."
    )


# ==========================================
# MAIN
# ==========================================

def main():
    if (
        not BOT_TOKEN
        or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE"
    ):
        raise RuntimeError(
            "Please add your Telegram bot token in config.py."
        )

    init_db()

    logger.info("Database initialized.")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register private-chat-only user features.
    register_user_handlers(application)

    # Admin command is private-chat-only.
    application.add_handler(
        CommandHandler(
            "admin",
            admin_command,
        )
    )

    application.add_error_handler(
        error_handler
    )

    logger.info(
        "SF ARMY 10K Giveaway Bot is starting."
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
