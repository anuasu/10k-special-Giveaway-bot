from database import (
    get_user,
    redeem_code,
    get_redeem_history,
)


def redeem_user_code(user_id, code):
    """Redeem a code for a registered user."""

    code = str(code or "").strip()

    if not code:
        return {
            "success": False,
            "reason": "empty_code",
            "message": "❌ Please enter a valid redeem code.",
        }

    user = get_user(user_id)

    if not user:
        return {
            "success": False,
            "reason": "user_not_found",
            "message": "❌ Please open the bot and use /start first.",
        }

    if not user.get("verified"):
        return {
            "success": False,
            "reason": "not_verified",
            "message": (
                "⚠️ Please join all required channels and groups "
                "and verify your membership before redeeming a code."
            ),
        }

    try:
        result = redeem_code(user_id, code)

        if result:
            return {
                "success": True,
                "reason": "redeemed",
                "message": "✅ <b>Redeem Code Accepted!</b>\n\n"
                           "Your code has been redeemed successfully.",
                "result": result,
            }

        return {
            "success": False,
            "reason": "invalid_or_used",
            "message": (
                "❌ This code is invalid, expired, unavailable, "
                "or already redeemed by you."
            ),
        }

    except Exception:
        return {
            "success": False,
            "reason": "error",
            "message": (
                "⚠️ Something went wrong while redeeming your code. "
                "Please try again later."
            ),
        }


def get_user_redeem_history(user_id):
    """Return the redeem history for a user."""

    try:
        history = get_redeem_history(user_id=user_id)
        return history or []
    except Exception:
        return []


def format_redeem_history(user_id):
    """Format a user's redeem history as an HTML message."""

    history = get_user_redeem_history(user_id)

    if not history:
        return (
            "🎟️ <b>Redeem History</b>\n\n"
            "You haven't redeemed any codes yet."
        )

    lines = [
        "🎟️ <b>Redeem History</b>",
        "",
    ]

    for index, item in enumerate(history, start=1):
        code = escape_html(item.get("code", "Unknown"))
        status = escape_html(item.get("status", "Redeemed"))
        redeemed_at = escape_html(
            item.get("redeemed_at", item.get("created_at", "Unknown"))
        )

        lines.append(
            f"{index}. <code>{code}</code>\n"
            f"   📌 Status: {status}\n"
            f"   🕒 Date: {redeemed_at}"
        )
        lines.append("")

    return "\n".join(lines)


def escape_html(value):
    """Escape user or database values before sending HTML messages."""

    value = str(value or "")
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
