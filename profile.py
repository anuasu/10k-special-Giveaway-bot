from database import (
    get_user,
    get_referral_counts,
    get_user_rank,
)
from helpers import (
    get_display_name,
    get_username,
    get_qualification_status,
    get_qualification_text,
    get_referral_link,
    get_coins_text,
    get_rank_text,
)
from config import QUALIFICATION_REFERRALS


def get_profile_data(user_id, bot_username):
    """Collect all data needed to display a user's profile."""

    user_id = int(user_id)
    user = get_user(user_id)

    if not user:
        return None

    referral_counts = get_referral_counts(user_id)

    verified_referrals = referral_counts["verified_referrals"]
    pending_referrals = referral_counts["pending_referrals"]

    rank = get_user_rank(user_id)

    return {
        "user_id": user_id,
        "name": get_display_name(user),
        "username": get_username(user.get("username")),
        "total_coins": user.get("total_coins", 0),
        "verified": bool(user.get("verified", 0)),
        "verified_referrals": verified_referrals,
        "pending_referrals": pending_referrals,
        "rank": rank,
        "rank_text": get_rank_text(rank),
        "qualified": get_qualification_status(verified_referrals),
        "qualification_text": get_qualification_text(
            verified_referrals
        ),
        "referral_link": get_referral_link(
            bot_username,
            user_id,
        ),
        "required_referrals": QUALIFICATION_REFERRALS,
    }


def format_profile_message(profile):
    """Format profile information as a Telegram MarkdownV2 message."""

    if not profile:
        return "⚠️ Profile not found. Please start the bot again."

    # Escape user-provided text to avoid MarkdownV2 parsing errors.
    def escape_markdown(text):
        special_chars = r"_*[]()~`>#+-=|{}.!\\"
        text = str(text)
        return "".join(
            "\\" + char if char in special_chars else char
            for char in text
        )

    name = escape_markdown(profile["name"])
    username = escape_markdown(profile["username"])
    user_id = profile["user_id"]
    coins = profile["total_coins"]
    verified = profile["verified_referrals"]
    pending = profile["pending_referrals"]
    rank = escape_markdown(profile["rank_text"])
    qualification = escape_markdown(
        profile["qualification_text"]
    )
    referral_link = profile["referral_link"]

    if profile["verified"]:
        verification_status = "✅ Verified"
    else:
        verification_status = "⏳ Not Verified"

    message = (
        "👤 *MY PROFILE*\n\n"
        f"📝 *Name:* {name}\n"
        f"🔗 *Username:* {username}\n"
        f"🆔 *User ID:* `{user_id}`\n"
        f"💰 *Total Coins:* {coins:,}\n"
        f"🏆 *Current Rank:* {rank}\n"
        f"👥 *Verified Referrals:* {verified}\n"
        f"⏳ *Pending Referrals:* {pending}\n"
        f"🎯 *Qualification:* {qualification}\n"
        f"🔐 *Account Status:* {verification_status}\n\n"
        "🔗 *Your Referral Link:*\n"
        f"`{referral_link}`\n\n"
        f"📌 Qualification requires at least "
        f"{profile['required_referrals']} verified referrals."
    )

    return message


def get_profile_message(user_id, bot_username):
    """Return the formatted profile message."""

    profile = get_profile_data(
        user_id=user_id,
        bot_username=bot_username,
    )

    return format_profile_message(profile)
