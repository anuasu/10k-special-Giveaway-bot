from database import (
    get_user,
    claim_welcome_bonus,
    claim_daily_bonus,
)
from config import WELCOME_BONUS, DAILY_BONUS
from helpers import get_current_date


def claim_welcome_bonus_for_user(user_id):
    """
    Grants the welcome bonus once after the user has been verified.
    Membership verification must be completed by the bot handler first.
    """
    user = get_user(user_id)

    if not user:
        return {
            "success": False,
            "reason": "user_not_found",
            "coins": 0,
            "message": "❌ User account not found. Please use /start first.",
        }

    if not user.get("verified"):
        return {
            "success": False,
            "reason": "not_verified",
            "coins": 0,
            "message": (
                "⚠️ Please join all required channels and groups, "
                "then verify your membership first."
            ),
        }

    if user.get("welcome_bonus_claimed"):
        return {
            "success": False,
            "reason": "already_claimed",
            "coins": 0,
            "message": "ℹ️ Your welcome bonus has already been claimed.",
        }

    success = claim_welcome_bonus(
        user_id=user_id,
        amount=WELCOME_BONUS,
    )

    if success:
        return {
            "success": True,
            "reason": "claimed",
            "coins": WELCOME_BONUS,
            "message": (
                "🎉 <b>Welcome Bonus Received!</b>\n\n"
                f"🪙 <b>+{WELCOME_BONUS} Coins</b> added to your balance."
            ),
        }

    return {
        "success": False,
        "reason": "already_claimed_or_not_verified",
        "coins": 0,
        "message": (
            "⚠️ Your welcome bonus could not be claimed. "
            "It may already have been credited."
        ),
    }


def claim_daily_bonus_for_user(user_id):
    """
    Grants the daily bonus once per India calendar day.
    The database checks verification and prevents duplicate claims.
    """
    user = get_user(user_id)

    if not user:
        return {
            "success": False,
            "reason": "user_not_found",
            "coins": 0,
            "message": "❌ User account not found. Please use /start first.",
        }

    if not user.get("verified"):
        return {
            "success": False,
            "reason": "not_verified",
            "coins": 0,
            "message": (
                "⚠️ Please join all required channels and groups, "
                "then verify your membership to claim your daily bonus."
            ),
        }

    today = get_current_date()

    if user.get("daily_bonus_date") == today:
        return {
            "success": False,
            "reason": "already_claimed",
            "coins": 0,
            "message": (
                "⏳ <b>Daily Bonus Already Claimed!</b>\n\n"
                "Please come back tomorrow for your next bonus."
            ),
        }

    success = claim_daily_bonus(
        user_id=user_id,
        amount=DAILY_BONUS,
    )

    if success:
        return {
            "success": True,
            "reason": "claimed",
            "coins": DAILY_BONUS,
            "message": (
                "🎁 <b>Daily Bonus Claimed!</b>\n\n"
                f"🪙 <b>+{DAILY_BONUS} Coins</b> added to your balance.\n"
                "🔄 Your next daily bonus will be available tomorrow."
            ),
        }

    return {
        "success": False,
        "reason": "already_claimed_or_not_verified",
        "coins": 0,
        "message": (
            "⚠️ Your daily bonus could not be claimed. "
            "Please try again later."
        ),
    }


def get_bonus_status(user_id):
    """
    Returns the current welcome and daily bonus status for a user.
    """
    user = get_user(user_id)

    if not user:
        return {
            "exists": False,
            "welcome_claimed": False,
            "daily_claimed": False,
            "welcome_bonus": WELCOME_BONUS,
            "daily_bonus": DAILY_BONUS,
        }

    today = get_current_date()

    return {
        "exists": True,
        "verified": bool(user.get("verified")),
        "welcome_claimed": bool(user.get("welcome_bonus_claimed")),
        "daily_claimed": user.get("daily_bonus_date") == today,
        "welcome_bonus": WELCOME_BONUS,
        "daily_bonus": DAILY_BONUS,
    }
