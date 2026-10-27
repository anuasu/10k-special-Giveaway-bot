from config import ADMIN_IDS
from database import (
    get_user,
    get_dashboard_stats,
    add_coins,
    deduct_coins,
    get_coin_transactions,
    get_all_users,
)


def is_admin(user_id):
    """Check whether a Telegram user is an authorized admin."""
    try:
        return int(user_id) in {int(admin_id) for admin_id in ADMIN_IDS}
    except (TypeError, ValueError):
        return False


def get_admin_dashboard():
    """Return the current bot dashboard statistics."""
    try:
        stats = get_dashboard_stats()
        return {
            "success": True,
            "stats": stats or {},
        }
    except Exception as error:
        return {
            "success": False,
            "error": str(error),
            "stats": {},
        }


def format_admin_dashboard():
    """Format dashboard statistics as an HTML message."""
    result = get_admin_dashboard()

    if not result["success"]:
        return "⚠️ <b>Dashboard unavailable.</b> Please try again later."

    stats = result["stats"]

    total_users = stats.get("total_users", 0)
    verified_users = stats.get("verified_users", 0)
    total_coins = stats.get("total_coins", 0)
    total_referrals = stats.get("total_referrals", 0)
    pending_referrals = stats.get("pending_referrals", 0)

    return (
        "📊 <b>SF ARMY ADMIN DASHBOARD</b>\n\n"
        f"👥 Total Users: <b>{total_users:,}</b>\n"
        f"✅ Verified Users: <b>{verified_users:,}</b>\n"
        f"🪙 Coins in Circulation: <b>{total_coins:,}</b>\n"
        f"👤 Verified Referrals: <b>{total_referrals:,}</b>\n"
        f"⏳ Pending Referrals: <b>{pending_referrals:,}</b>"
    )


def get_user_details(user_id):
    """Get a registered user's details."""
    try:
        user = get_user(int(user_id))

        if not user:
            return {
                "success": False,
                "message": "❌ User not found in the database.",
                "user": None,
            }

        return {
            "success": True,
            "message": "✅ User found.",
            "user": user,
        }

    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "❌ Please provide a valid numeric Telegram user ID.",
            "user": None,
        }


def add_user_coins(user_id, amount, admin_id, reason="Admin adjustment"):
    """Add coins to a user after validating the request."""
    if not is_admin(admin_id):
        return {
            "success": False,
            "message": "⛔ You are not authorized to perform this action.",
        }

    try:
        user_id = int(user_id)
        amount = int(amount)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "❌ User ID and coin amount must be numbers.",
        }

    if amount <= 0:
        return {
            "success": False,
            "message": "❌ Coin amount must be greater than zero.",
        }

    if not get_user(user_id):
        return {
            "success": False,
            "message": "❌ User not found.",
        }

    try:
        success = add_coins(
            user_id=user_id,
            amount=amount,
            reason=f"{reason} (Admin ID: {admin_id})",
        )

        if success:
            updated_user = get_user(user_id)
            balance = int(updated_user.get("total_coins", 0))

            return {
                "success": True,
                "message": (
                    "✅ <b>Coins Added Successfully!</b>\n\n"
                    f"👤 User ID: <code>{user_id}</code>\n"
                    f"➕ Added: <b>{amount:,} Coins</b>\n"
                    f"💰 New Balance: <b>{balance:,} Coins</b>"
                ),
                "balance": balance,
            }

        return {
            "success": False,
            "message": "❌ Coins could not be added.",
        }

    except Exception:
        return {
            "success": False,
            "message": "⚠️ An error occurred while adding coins.",
        }


def deduct_user_coins(user_id, amount, admin_id, reason="Admin adjustment"):
    """Deduct coins from a user after validating the request."""
    if not is_admin(admin_id):
        return {
            "success": False,
            "message": "⛔ You are not authorized to perform this action.",
        }

    try:
        user_id = int(user_id)
        amount = int(amount)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "❌ User ID and coin amount must be numbers.",
        }

    if amount <= 0:
        return {
            "success": False,
            "message": "❌ Coin amount must be greater than zero.",
        }

    if not get_user(user_id):
        return {
            "success": False,
            "message": "❌ User not found.",
        }

    try:
        success = deduct_coins(
            user_id=user_id,
            amount=amount,
            reason=f"{reason} (Admin ID: {admin_id})",
        )

        if success:
            updated_user = get_user(user_id)
            balance = int(updated_user.get("total_coins", 0))

            return {
                "success": True,
                "message": (
                    "✅ <b>Coins Deducted Successfully!</b>\n\n"
                    f"👤 User ID: <code>{user_id}</code>\n"
                    f"➖ Deducted: <b>{amount:,} Coins</b>\n"
                    f"💰 New Balance: <b>{balance:,} Coins</b>"
                ),
                "balance": balance,
            }

        return {
            "success": False,
            "message": (
                "❌ Coins could not be deducted. "
                "The user may not have enough coins."
            ),
        }

    except Exception:
        return {
            "success": False,
            "message": "⚠️ An error occurred while deducting coins.",
        }


def get_user_transactions(user_id, limit=20):
    """Return a user's recent coin transactions."""
    try:
        user_id = int(user_id)
        limit = max(1, min(int(limit), 100))

        if not get_user(user_id):
            return []

        transactions = get_coin_transactions(user_id)

        return (transactions or [])[:limit]

    except (TypeError, ValueError):
        return []


def get_user_list():
    """Return all registered users for admin tools."""
    try:
        return get_all_users() or []
    except Exception:
        return []
