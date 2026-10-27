from config import (
    REWARD_SYSTEM_ENABLED,
    REWARD_COMING_SOON_TEXT,
    QUALIFICATION_REFERRALS,
)

from database import get_user, get_referral_counts


def get_user_reward_status(user_id):
    """Get a user's eligibility status for future rewards."""

    user = get_user(user_id)

    if not user:
        return {
            "success": False,
            "reason": "user_not_found",
            "message": "❌ Please use /start to register first.",
        }

    referral_data = get_referral_counts(user_id) or {}

    verified_referrals = int(
        referral_data.get("verified_referrals", 0) or 0
    )

    qualified = verified_referrals >= QUALIFICATION_REFERRALS

    return {
        "success": True,
        "user_id": int(user_id),
        "verified": bool(user.get("verified")),
        "total_coins": int(user.get("total_coins", 0) or 0),
        "verified_referrals": verified_referrals,
        "required_referrals": QUALIFICATION_REFERRALS,
        "qualified": qualified,
        "reward_system_enabled": REWARD_SYSTEM_ENABLED,
    }


def get_rewards_message(user_id):
    """Generate the Rewards menu message."""

    status = get_user_reward_status(user_id)

    if not status["success"]:
        return status["message"]

    if not REWARD_SYSTEM_ENABLED:
        return (
            "🎁 <b>SF ARMY REWARDS</b>\n\n"
            f"{REWARD_COMING_SOON_TEXT}\n\n"
            "🪙 Keep collecting coins and inviting friends.\n"
            f"🎯 Qualification Target: "
            f"<b>{QUALIFICATION_REFERRALS} Verified Referrals</b>\n\n"
            "📢 Further reward details will be announced officially."
        )

    verified_referrals = status["verified_referrals"]
    qualified = status["qualified"]

    qualification_text = (
        "✅ Qualified"
        if qualified
        else "⏳ Not Qualified Yet"
    )

    return (
        "🎁 <b>SF ARMY REWARDS</b>\n\n"
        f"🪙 Total Coins: <b>{status['total_coins']:,}</b>\n"
        f"👥 Verified Referrals: <b>{verified_referrals}</b>\n"
        f"🎯 Required Referrals: "
        f"<b>{QUALIFICATION_REFERRALS}</b>\n"
        f"📌 Status: <b>{qualification_text}</b>\n\n"
        "ℹ️ Final reward distribution details will be announced "
        "by the administration."
    )


def is_user_qualified(user_id):
    """Check whether the user meets the referral qualification target."""

    status = get_user_reward_status(user_id)

    if not status["success"]:
        return False

    return (
        status["verified"]
        and status["verified_referrals"] >= QUALIFICATION_REFERRALS
    )
