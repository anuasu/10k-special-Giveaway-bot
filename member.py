from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

from config import CHANNELS


async def check_single_membership(bot, user_id, chat_id):
    """
    Check whether a user has joined a specific channel or group.
    Returns True only when membership is confirmed.
    """
    try:
        member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id,
        )

        return member.status in ("member", "administrator", "creator")

    except TelegramError:
        # If membership cannot be checked, do not assume the user joined.
        return False


async def check_all_memberships(bot, user_id):
    """
    Check membership in every required channel/group.
    Returns a dictionary containing the verification result.
    """
    joined = []
    missing = []
    errors = []

    for channel in CHANNELS:
        chat_id = channel.get("chat_id")
        name = channel.get("name", "Required Chat")

        is_joined = await check_single_membership(
            bot=bot,
            user_id=user_id,
            chat_id=chat_id,
        )

        if is_joined:
            joined.append(name)
        else:
            missing.append(channel)
            errors.append(name)

    return {
        "verified": len(missing) == 0,
        "joined": joined,
        "missing": missing,
        "total_required": len(CHANNELS),
        "total_joined": len(joined),
        "errors": errors,
    }


def get_membership_keyboard(missing_channels=None):
    """
    Create join buttons for required channels/groups and a Verify button.
    """
    channels = missing_channels if missing_channels is not None else CHANNELS

    keyboard = []

    for channel in channels:
        name = channel.get("name", "Join Channel")
        url = channel.get("url")

        if url:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"➕ Join {name}",
                    url=url,
                )
            ])

    keyboard.append([
        InlineKeyboardButton(
            text="✅ Verify Membership",
            callback_data="verify_membership",
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def format_membership_message(result=None):
    """
    Generate the message shown when membership verification is required.
    """
    if result and result.get("verified"):
        return (
            "✅ <b>Membership Verified Successfully!</b>\n\n"
            "You're all set. You can now access the bot features."
        )

    if result:
        joined = result.get("total_joined", 0)
        total = result.get("total_required", len(CHANNELS))

        return (
            "🔒 <b>Join Required Channels & Groups</b>\n\n"
            "Please join all the channels and groups listed below.\n"
            "After joining, tap <b>Verify Membership</b>.\n\n"
            f"📊 Joined: <b>{joined}/{total}</b>\n\n"
            "⚠️ If you've already joined but verification fails, "
            "please try again in a moment."
        )

    return (
        "🔒 <b>Membership Verification Required</b>\n\n"
        "Please join all required channels and groups, "
        "then tap <b>Verify Membership</b>."
    )


async def verify_user_membership(bot, user_id):
    """
    Convenience function for handlers.
    Checks all required chats and returns the result with a message.
    """
    result = await check_all_memberships(
        bot=bot,
        user_id=user_id,
    )

    result["message"] = format_membership_message(result)
    result["keyboard"] = (
        None
        if result["verified"]
        else get_membership_keyboard(result["missing"])
    )

    return result
